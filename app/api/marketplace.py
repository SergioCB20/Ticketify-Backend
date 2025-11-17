from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from typing import List, Optional
import math
import traceback
from uuid import UUID
from datetime import timedelta, datetime 
from pprint import pprint
from fastapi.responses import JSONResponse
from app.schemas.marketplace import MarketplaceListingResponse
from app.core.database import get_db
from app.core.dependencies import get_current_active_user 
from app.core.dependencies import get_current_active_user, get_attendee_user
from app.models.user import User
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.models.event import Event
from app.models.ticket import Ticket, TicketStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus 
from app.services.marketplace_service import MarketplaceService 
import uuid
# Importar utilidades de imagen
from app.utils.image_utils import process_nested_user_photo

# (Asumo que tus schemas están en sus propios archivos como planeamos)
from app.schemas.marketplace import (
    MarketplaceListingResponse, 
    PaginatedMarketplaceListings,
    MarketplaceListingCreate 
)

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

# --- ENDPOINT GET (Para ver el listado) ---
@router.get("/listings", response_model=PaginatedMarketplaceListings)
async def get_active_listings(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    """
    Obtener todos los listados de reventa ACTIVOS y paginados.
    """
    try:
        # Query base: Solo listados ACTIVOS
        query = (
            select(MarketplaceListing)
            .join(MarketplaceListing.event) # Join con Evento
            .options(
                joinedload(MarketplaceListing.seller), # Cargar datos del vendedor
                joinedload(MarketplaceListing.event),   # Cargar datos del evento
                joinedload(MarketplaceListing.ticket).joinedload(Ticket.ticket_type)  # Cargar tipo de ticket
            )
            .where(MarketplaceListing.status == ListingStatus.ACTIVE)
        )
        
        # Filtro de búsqueda (busca en título del listado o título del evento)
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(MarketplaceListing.title).like(search_term),
                    func.lower(Event.title).like(search_term)
                )
            )

        # Contar el total de items (antes de paginar)
        total_query = select(func.count()).select_from(query.subquery())
        total = db.execute(total_query).scalar() 
        
        if total is None:
            total = 0

        # Calcular paginación
        total_pages = math.ceil(total / page_size)
        offset = (page - 1) * page_size
        
        # Aplicar paginación y ejecutar query
        listings = db.scalars(query.order_by(MarketplaceListing.created_at.desc()).offset(offset).limit(page_size)).unique().all()
        
        # 🔧 PROCESAR FOTOS DE PERFIL: Convertir bytes a base64
        for listing in listings:
            # Procesar foto del vendedor si existe
            process_nested_user_photo(listing, 'seller', 'profilePhoto')
        
        # Crear respuesta
        response_data = PaginatedMarketplaceListings(
            items=[MarketplaceListingResponse.model_validate(listing) for listing in listings],
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages,
        )
        return response_data

    except Exception as e:
        print(f"Error al obtener listados del marketplace: {e}")
        traceback.print_exc() 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al cargar los listados."
        )


# --- ENDPOINT POST (Para vender un ticket) ---
@router.post("/listings", response_model=MarketplaceListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    listing_data: MarketplaceListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # 1. VALIDACIÓN: Buscar el ticket que el usuario quiere vender
    ticket_to_sell = db.query(Ticket).filter(
        Ticket.id == listing_data.ticketId
    ).options(
        joinedload(Ticket.event) # Cargar el evento para obtener título y fecha
    ).first()

    # 2. VALIDACIÓN: ¿Existe el ticket?
    if not ticket_to_sell:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ticket que intentas vender no existe."
        )

    # 3. VALIDACIÓN: ¿El ticket le pertenece al usuario?
    if ticket_to_sell.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes vender un ticket que no te pertenece."
        )

    # 4. VALIDACIÓN: ¿El ticket está ACTIVO?
    if ticket_to_sell.status != TicketStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No puedes vender un ticket que ya está {ticket_to_sell.status.value}."
        )

    # 6. VALIDACIÓN: ¿El ticket ya está en reventa?
    existing_listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.ticket_id == ticket_to_sell.id,
        MarketplaceListing.status == ListingStatus.ACTIVE
    ).first()
    
    if existing_listing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este ticket ya está publicado en el marketplace."
        )

    # 7. CREACIÓN: Si todo está bien, creamos el listado
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
    
    # 🔧 Procesar foto del vendedor antes de retornar
    process_nested_user_photo(new_listing, 'seller', 'profilePhoto')
    
    return new_listing


# --- ENDPOINT POST (Para comprar un ticket) ---
@router.post("/listings/{listing_id}/buy", response_model=dict)
async def buy_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_attendee_user)
):
    """
    Inicia el proceso de compra de un ticket en reventa.
    (Versión simplificada que simula un pago exitoso)
    """
    
    listing = db.query(MarketplaceListing).filter(
        MarketplaceListing.id == listing_id,
        MarketplaceListing.status == ListingStatus.ACTIVE
    ).options(
        joinedload(MarketplaceListing.ticket).joinedload(Ticket.event)
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Este listado no está disponible.")

    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes comprar tu propio ticket.")

    # --- SIMULACIÓN DE PAGO ---
    # 1. Crear el registro del Pago
    new_payment = Payment(
        amount=listing.price,
        paymentMethod=PaymentMethod.CREDIT_CARD,
        transactionId=f"txn_resale_{uuid.uuid4()}",
        status=PaymentStatus.COMPLETED,
        paymentDate=datetime.utcnow(),
        user_id=current_user.id
    )
    db.add(new_payment)
    db.flush()

    # 2. Llamar al servicio de transferencia atómica
    try:
        service = MarketplaceService(db)
        new_ticket = service.transfer_ticket_on_purchase(
            listing=listing,
            buyer=current_user,
            payment_id=new_payment.id
        )
        
        return {
            "success": True, 
            "message": "¡Compra completada! Se ha generado un nuevo ticket.",
            "newTicketId": new_ticket.id,
            "listingId": listing.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la transferencia: {e}")


# --- ENDPOINT DELETE (Para retirar un ticket del marketplace) ---
@router.delete("/listings/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancela/retira un listing del marketplace.
    Solo el vendedor puede cancelar su propio listing.
    """
    
    # 1. Buscar el listing
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
    
    # 2. Verificar que el usuario sea el vendedor
    if listing.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cancelar un listing que no te pertenece."
        )
    
    # 3. Verificar que el listing esté activo
    if listing.status != ListingStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No puedes cancelar un listing que está {listing.status.value}."
        )
    
    # 4. Cancelar el listing y reactivar el ticket
    try:
        listing.status = ListingStatus.CANCELLED
        
        # Reactivar el ticket del vendedor
        ticket = listing.ticket
        ticket.status = TicketStatus.ACTIVE
        ticket.isValid = True
        
        db.add(listing)
        db.add(ticket)
        db.commit()
        
        return None  # 204 No Content
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar el listing: {e}"
        )
