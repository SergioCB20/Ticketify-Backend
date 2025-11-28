from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from typing import List, Optional
from uuid import UUID
from datetime import timedelta, datetime, timezone
from fastapi.responses import JSONResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_attendee_user
from app.models.user import User
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.models.event import Event
from app.models.ticket import Ticket, TicketStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus 
from app.services.marketplace_service import MarketplaceService 
from app.services.payment_service import PaymentService
from app.core.config import settings
from app.utils.image_utils import process_nested_user_photo
from app.schemas.marketplace import (
    ListingResponse, 
    CreateListingRequest,
    UpdateListingRequest,
    PaginatedMarketplaceListings,
    MarketplacePreferenceRequest,
    MarketplacePreferenceResponse,
    MarketplacePurchaseResponse,
    MarketplacePurchaseRequest
)
from decimal import Decimal
import uuid
import logging
import mercadopago
import math
import traceback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.get("/listings", response_model=PaginatedMarketplaceListings)
async def get_active_listings(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    order_by: Optional[str] = Query(None),
):
    """
    Obtener todos los listados de reventa ACTIVOS y paginados.
    """
    try:
        query = (
            select(MarketplaceListing)
            .join(Event, MarketplaceListing.event_id == Event.id)
            .options(
                joinedload(MarketplaceListing.seller),
                joinedload(MarketplaceListing.event),
                joinedload(MarketplaceListing.ticket).joinedload(Ticket.ticket_type)
            )
            .where(
                MarketplaceListing.status == ListingStatus.ACTIVE,
                MarketplaceListing.expires_at > datetime.utcnow(),
                Event.startDate >= datetime.utcnow()  # Filtrar eventos que ya empezaron
            )
        )
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(MarketplaceListing.title).like(search_term),
                    func.lower(Event.title).like(search_term)
                )
            )
        
        if min_price is not None:
            query = query.where(MarketplaceListing.price >= min_price)
        
        if max_price is not None:
            query = query.where(MarketplaceListing.price <= max_price)

        total_query = select(func.count()).select_from(query.subquery())
        total = db.execute(total_query).scalar() 
        
        if total is None:
            total = 0

        total_pages = math.ceil(total / page_size)
        offset = (page - 1) * page_size
        
        if order_by == "price_asc":
            query = query.order_by(MarketplaceListing.price.asc())
        elif order_by == "price_desc":
            query = query.order_by(MarketplaceListing.price.desc())
        else:
            query = query.order_by(MarketplaceListing.created_at.desc())
        
        listings = db.scalars(query.offset(offset).limit(page_size)).unique().all()
        
        # --- CORRECCIÓN AQUÍ ---
        # Antes tenías settings.BACKEND_URL, lo cambiamos a "seller" para indicar
        # que debe procesar la foto del usuario que está en el campo 'seller'.
        for listing in listings:
            process_nested_user_photo(listing, "seller")
        # -----------------------
        
        response_data = PaginatedMarketplaceListings(
            items=[ListingResponse.model_validate(listing) for listing in listings],
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )

        return response_data
        
    except Exception as e:
        logger.error(f"Error al obtener listados del marketplace: {e}", exc_info=True)
        traceback.print_exc() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al cargar los listados."
        )

@router.post("/listings", response_model=ListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: CreateListingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crear un nuevo listado de reventa en el marketplace.
    """
    ticket_to_sell = db.query(Ticket).filter(
        Ticket.id == listing_data.ticketId
    ).options(
        joinedload(Ticket.event)
    ).first()

    if not ticket_to_sell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ticket que intentas vender no existe."
        )

    if ticket_to_sell.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes vender un ticket que no te pertenece."
        )

    if ticket_to_sell.status != TicketStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No puedes vender un ticket que ya está {ticket_to_sell.status.value}."
        )

    # Validar precio máximo (150% del precio original)
    original_price = ticket_to_sell.price
    max_allowed_price = original_price * Decimal("1.5")
    min_allowed_price = original_price * Decimal("0.5")
    
    if listing_data.price > max_allowed_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El precio máximo permitido es S/ {max_allowed_price:.2f} (150% del precio original)"
        )
    
    if listing_data.price < min_allowed_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El precio mínimo permitido es S/ {min_allowed_price:.2f} (50% del precio original)"
        )
    
    existing_listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.ticket_id == ticket_to_sell.id,
        MarketplaceListing.status == ListingStatus.ACTIVE
    ).first()
    
    if existing_listing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este ticket ya está publicado en el marketplace."
        )

    new_listing = MarketplaceListing(
        title=f"Reventa de entrada para: {ticket_to_sell.event.title}",
        description=listing_data.description,
        price=listing_data.price,
        original_price=ticket_to_sell.price,
        is_negotiable=False, 
        status=ListingStatus.ACTIVE,
        seller_id=current_user.id,
        ticket_id=ticket_to_sell.id,
        event_id=ticket_to_sell.event_id,
        expires_at=ticket_to_sell.event.startDate - timedelta(hours=1)
    )
    
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    
    process_nested_user_photo(new_listing, 'seller', 'profilePhoto')
    
    return new_listing


@router.post("/listings/{listing_id}/create-preference", response_model=MarketplacePurchaseResponse)
async def create_marketplace_preference(
    listing_id: UUID,
    request: MarketplacePurchaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_attendee_user)
):
    """
    Crea una preferencia de pago de MercadoPago para comprar un ticket del marketplace.
    El dinero va al vendedor con una comisión para la plataforma.
    """
    
    listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.id == listing_id,
        MarketplaceListing.status == ListingStatus.ACTIVE
    ).options(
        joinedload(MarketplaceListing.ticket).joinedload(Ticket.event),
        joinedload(MarketplaceListing.seller)
    ).first()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este listado no está disponible."
        )

    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes comprar tu propio ticket."
        )

    seller = listing.seller
    if not seller.isMercadopagoConnected:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vendedor no ha conectado su cuenta de MercadoPago."
        )

    try:
        items_list = [{
            "title": f"{listing.title}",
            "quantity": 1,
            "unit_price": float(listing.price),
            "currency_id": "PEN"
        }]

        # Calcular comisión de la plataforma (5%)
        platform_fee = Decimal(str(listing.price)) * Decimal("0.05")

        payment_service = PaymentService()
        preference = payment_service.create_marketplace_preference(
            listing_id=str(listing.id),
            items=items_list,
            buyer_email=current_user.email,
            buyer_id=str(current_user.id),
            seller=seller,
            platform_fee=platform_fee
        )

        logger.info(f"✅ Preferencia de marketplace creada: {preference['id']} para listing {listing.id}")

        return MarketplacePurchaseResponse(
            listingId=listing.id,
            initPoint=preference["init_point"],
            preferenceId=preference["id"]
        )

    except Exception as e:
        logger.error(f"❌ Error al crear preferencia de marketplace: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la preferencia de pago: {str(e)}"
        )


@router.post("/webhook")
async def marketplace_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Recibe notificaciones de pago del marketplace.
    Procesa la transferencia del ticket cuando el pago es aprobado.
    ACTUALIZADO: Sigue la misma lógica que purchases/webhook
    """
    try:
        body = await request.json()
        logger.info(f"🔔 Webhook marketplace recibido: {body}")
        
        topic = body.get("topic")
        action = body.get("action")
        
        # Solo procesar notificaciones de pago
        if topic == "payment" or action == "payment.created":
            payment_id = body.get("data", {}).get("id")
            if not payment_id:
                logger.warning("⚠️ Webhook sin payment_id")
                return {"status": "ok"}

            try:
                # Inicializar SDK de plataforma para consultar el pago
                sdk = mercadopago.SDK(settings.MERCADOPAGO_PRODUCER_TOKEN)
                payment_data = sdk.payment().get(payment_id)
                
                if payment_data["status"] != 200:
                    logger.error(f"❌ Error al consultar pago {payment_id}: {payment_data}")
                    raise HTTPException(status_code=500, detail="Error al consultar pago")
                
                payment_info = payment_data["response"]
                status_detail = payment_info.get("status")
                external_reference = payment_info.get("external_reference")

                if not external_reference:
                    logger.warning(f"⚠️ Pago {payment_id} sin external_reference")
                    return {"status": "ok"}

                # Parsear el external_reference
                # Formato: "LISTING_{listing_id}_BUYER_{buyer_id}"
                parts = external_reference.split("_")
                if len(parts) != 4 or parts[0] != "LISTING" or parts[2] != "BUYER":
                    logger.error(f"❌ Formato de external_reference inválido: {external_reference}")
                    return {"status": "error", "message": "Formato de external_reference inválido"}
                
                listing_id = parts[1]
                buyer_id = parts[3]

                # Buscar el listing en nuestra BBDD
                listing = db.query(MarketplaceListing).filter(
                    MarketplaceListing.id == listing_id
                ).options(
                    joinedload(MarketplaceListing.ticket)
                ).first()
                
                if not listing:
                    logger.error(f"❌ Listing {listing_id} no encontrado")
                    raise HTTPException(status_code=404, detail=f"Listing {listing_id} no encontrado")

                # Buscar el comprador
                buyer = db.query(User).filter(User.id == buyer_id).first()
                
                if not buyer:
                    logger.error(f"❌ Comprador {buyer_id} no encontrado")
                    raise HTTPException(status_code=404, detail="Comprador no encontrado")

                # SI EL PAGO FUE APROBADO
                if status_detail == "approved":
                    logger.info(f"✅ Pago aprobado para listing {listing.id}")
                    
                    # Preparar información del pago (igual que en purchases)
                    payment_info_dict = {
                        "id": payment_info["id"],
                        "amount": payment_info["transaction_amount"],
                        "status": payment_info["status"],
                        "status_detail": payment_info.get("status_detail"),
                        "payment_method_id": payment_info.get("payment_method_id"),
                        "payment_type_id": payment_info.get("payment_type_id")
                    }
                    
                    # Calcular comisión de la plataforma (5%)
                    platform_fee = Decimal(str(listing.price)) * Decimal("0.05")
                    
                    # Usar el servicio para procesar el pago y transferir el ticket
                    service = MarketplaceService(db)
                    new_ticket = service.create_marketplace_payment_and_transfer(
                        listing=listing,
                        buyer=buyer,
                        payment_info=payment_info_dict,
                        platform_fee=platform_fee
                    )
                    
                    logger.info(f"✅ Ticket transferido exitosamente a {buyer.email}")
                
                # Manejar otros estados
                elif status_detail == "rejected":
                    logger.info(f"⚠️ Pago rechazado para listing {listing.id}")
                    # Opcional: marcar el listing como disponible de nuevo
                
                elif status_detail == "pending":
                    logger.info(f"⏳ Pago pendiente para listing {listing.id}")

            except Exception as e:
                db.rollback()
                logger.error(f"❌ Error procesando webhook de marketplace: {str(e)}")
                raise HTTPException(status_code=500, detail="Error al procesar webhook")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Error general en webhook marketplace: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.delete("/listings/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancela/retira un listing del marketplace.
    """
    
    listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.id == listing_id
    ).options(
        joinedload(MarketplaceListing.ticket)
    ).first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El listing no existe."
        )
    
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cancelar un listing que no te pertenece."
        )
    
    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No puedes cancelar un listing que está {listing.status.value}."
        )
    
    try:
        listing.status = ListingStatus.CANCELLED
        
        ticket = listing.ticket
        ticket.status = TicketStatus.ACTIVE
        ticket.isValid = True
        
        db.add(listing)
        db.add(ticket)
        db.commit()
        
        return None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar el listing: {e}"
        )


@router.get("/listings/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtener el detalle de un listado específico del marketplace.
    """
    listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.id == listing_id
    ).options(
        joinedload(MarketplaceListing.seller),
        joinedload(MarketplaceListing.event),
        joinedload(MarketplaceListing.ticket).joinedload(Ticket.ticket_type)
    ).first()

    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listado no encontrado"
        )
    
    # Procesar la URL de la foto del vendedor
    process_nested_user_photo(listing, "seller")
    
    return listing
