"""
API Endpoint para compras directas de tickets (no marketplace)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
import logging
import json

from app.core.database import get_db
from app.core.dependencies import get_attendee_user
from app.models.user import User
from app.models.event import Event
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.purchase import Purchase, PurchaseStatus
from app.models.promotion import Promotion
from app.schemas.purchase import (
    CreatePreferenceRequest,
    CreatePreferenceResponse,
    PurchaseDetailResponse
)
from app.services.payment_service import PaymentService
from app.services.purchase_service import PurchaseService
from app.core.config import settings
import mercadopago

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post("/create-preference", response_model=CreatePreferenceResponse)
async def create_purchase_preference(
    request: CreatePreferenceRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_attendee_user)
):
    """
    Crea una preferencia de pago en MercadoPago para compra directa de tickets.
    Soporta múltiples tipos de tickets en una sola transacción.
    
    **Flujo:**
    1. Valida evento y disponibilidad
    2. Valida código promocional (si se proporciona)
    3. Calcula monto total con descuentos
    4. Crea registro de compra en estado PENDING
    5. Genera preferencia de pago en MercadoPago
    6. Retorna init_point para redirigir al usuario
    """
    
    try:
        # 1. VALIDAR EVENTO
        event = db.query(Event).filter(Event.id == request.eventId).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El evento no existe"
            )
        
        # Verificar que el evento no haya pasado
        if event.startDate < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pueden comprar tickets para eventos pasados"
            )
        
        # 2. VALIDAR TIPOS DE TICKETS Y DISPONIBILIDAD
        ticket_selections = []
        items_list = []
        
        for ticket_sel in request.tickets:
            ticket_type = db.query(TicketType).filter(
                TicketType.id == ticket_sel.ticketTypeId,
                TicketType.event_id == event.id
            ).first()
            
            if not ticket_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"El tipo de ticket {ticket_sel.ticketTypeId} no existe para este evento"
                )
            
            # Verificar disponibilidad
            available = ticket_type.quantity_available - ticket_type.sold_quantity
            if available < ticket_sel.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Solo quedan {available} tickets disponibles de tipo {ticket_type.name}"
                )
            
            ticket_selections.append({
                'ticket_type': ticket_type,
                'quantity': ticket_sel.quantity
            })
            
            # Preparar items para MercadoPago
            items_list.append({
                "title": f"{ticket_type.name} - {event.title}",
                "quantity": ticket_sel.quantity,
                "unit_price": float(ticket_type.price),
                "currency_id": "PEN"
            })
        
        # 3. VALIDAR Y APLICAR PROMOCIÓN (si existe)
        promotion = None
        if request.promotionCode:
            promotion = db.query(Promotion).filter(
                Promotion.code == request.promotionCode.upper(),
                Promotion.event_id == event.id,
                Promotion.is_active == True
            ).first()
            
            if not promotion:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código promocional inválido o expirado"
                )
            
            # Verificar fecha de validez
            now = datetime.now(timezone.utc)
            if promotion.valid_from and now < promotion.valid_from:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La promoción aún no está activa"
                )
            
            if promotion.valid_until and now > promotion.valid_until:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La promoción ha expirado"
                )
            
            # Verificar límite de uso
            if promotion.max_uses and promotion.current_uses >= promotion.max_uses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La promoción ha alcanzado su límite de uso"
                )
        
        # 4. CALCULAR MONTO TOTAL
        amounts = PurchaseService.calculate_purchase_amount(
            ticket_selections=ticket_selections,
            promotion=promotion
        )
        
        # 5. CREAR REGISTRO DE COMPRA (PENDING)
        # Guardar las selecciones como JSON en notes
        ticket_selections_json = json.dumps([
            {
                "ticketTypeId": str(sel['ticket_type'].id),
                "quantity": sel['quantity'],
                "price": float(sel['ticket_type'].price)
            }
            for sel in ticket_selections
        ])
        
        purchase = Purchase(
            total_amount=amounts['total_amount'],
            subtotal=amounts['subtotal'],
            tax_amount=amounts['tax_amount'],
            service_fee=amounts['service_fee'],
            discount_amount=amounts['discount_amount'],
            quantity=amounts['quantity'],
            unit_price=amounts['subtotal'] / amounts['quantity'],  # Precio promedio
            status=PurchaseStatus.PENDING,
            payment_method=PaymentMethod.MERCADOPAGO,
            buyer_email=current_user.email,
            purchase_date=datetime.now(timezone.utc),
            user_id=current_user.id,
            event_id=event.id,
            ticket_type_id=None,  # Null para compras múltiples
            promotion_id=promotion.id if promotion else None,
            payment_id=None,
            notes=ticket_selections_json  # Guardar los tickets seleccionados
        )
        db.add(purchase)
        db.flush()
        
        try:
            # 6. CREAR PREFERENCIA DE PAGO
            payment_service = PaymentService()
            preference = payment_service.create_event_preference(
                purchase=purchase,
                items=items_list,
                buyer_email=current_user.email
            )
            
            # 7. Guardar el ID de preferencia en la compra
            purchase.mercadopago_preference_id = preference["id"]
            
            # Si hay promoción, incrementar el uso
            if promotion:
                promotion.current_uses += 1
            
            db.commit()
            db.refresh(purchase)
            
            logger.info(f"✅ Preferencia de pago creada: {preference['id']} para compra {purchase.id}")
            
            # 8. DEVOLVER EL INIT_POINT AL FRONTEND
            return CreatePreferenceResponse(
                purchaseId=purchase.id,
                init_point=preference["init_point"],
                preferenceId=preference["id"]
            )

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Error al crear preferencia: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear la preferencia de pago: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error general en create_preference: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud: {str(e)}"
        )


@router.post("/webhook")
async def mercadopago_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Recibe notificaciones de pago de MercadoPago.
    Procesa el pago y finaliza la compra cuando es aprobado.
    """
    try:
        body = await request.json()
        logger.info(f"🔔 Webhook recibido: {body}")
        
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

                # Buscar la compra en nuestra BBDD
                purchase = db.query(Purchase).filter(Purchase.id == external_reference).first()
                if not purchase:
                    logger.error(f"❌ Compra {external_reference} no encontrada")
                    raise HTTPException(status_code=404, detail=f"Compra {external_reference} no encontrada")

                # SI EL PAGO FUE APROBADO
                if status_detail == "approved":
                    logger.info(f"✅ Pago aprobado para compra {purchase.id}")
                    
                    payment_info_dict = {
                        "id": payment_info["id"],
                        "amount": payment_info["transaction_amount"],
                        "status": payment_info["status"],
                        "status_detail": payment_info.get("status_detail"),
                        "payment_method_id": payment_info.get("payment_method_id"),
                        "payment_type_id": payment_info.get("payment_type_id")
                    }
                    
                    # Llamar a nuestro servicio para finalizar la compra
                    PurchaseService.finalize_purchase_transaction(
                        db=db,
                        purchase=purchase,
                        payment_info=payment_info_dict
                    )
                    
                    db.commit()
                    logger.info(f"✅ Compra {purchase.id} finalizada exitosamente")
                
                # Manejar otros estados
                elif status_detail == "rejected":
                    purchase.status = PurchaseStatus.REJECTED
                    db.commit()
                    logger.info(f"⚠️ Pago rechazado para compra {purchase.id}")
                
                elif status_detail == "pending":
                    logger.info(f"⏳ Pago pendiente para compra {purchase.id}")

            except Exception as e:
                db.rollback()
                logger.error(f"❌ Error procesando webhook de MP: {str(e)}")
                raise HTTPException(status_code=500, detail="Error al procesar webhook")

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"❌ Error general en webhook: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.get("/my-purchases")
async def get_my_purchases(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_attendee_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las compras del usuario actual con paginación.
    """
    purchases, total = PurchaseService.get_user_purchases(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    
    return {
        "items": [purchase.to_dict() for purchase in purchases],
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": (total + page_size - 1) // page_size
    }


@router.get("/my-purchases/{purchase_id}", response_model=dict)
async def get_purchase_detail(
    purchase_id: UUID,
    current_user: User = Depends(get_attendee_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle de una compra específica del usuario.
    """
    try:
        purchase = PurchaseService.get_purchase_details(
            db=db,
            purchase_id=purchase_id,
            user_id=current_user.id
        )
        
        # Incluir información del evento y tickets
        event = db.query(Event).filter(Event.id == purchase.event_id).first()
        tickets = db.query(Ticket).filter(Ticket.purchase_id == purchase.id).all()
        
        result = purchase.to_dict()
        result["eventTitle"] = event.title if event else "Evento no encontrado"
        result["tickets"] = [ticket.to_dict() for ticket in tickets]
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
