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
    Crea una preferencia de pago en Mercado Pago y una orden de compra PENDING.
    """
    try:
        # 1. Llamar al servicio para crear la compra en BD
        purchase, mp_items = PurchaseService.create_pending_purchase(
            db=db,
            user_id=current_user.id,
            event_id=request.eventId,
            tickets_data=request.tickets,
            promotion_code=request.promotionCode
        )
        
        # Actualizar email del comprador (importante para MP)
        purchase.buyer_email = current_user.email
        db.commit()

        # 2. Instanciar servicio de pagos (Modo Agregador / Productor)
        payment_service = PaymentService()
        
        # 3. Crear la preferencia en Mercado Pago
        # Esto devuelve el diccionario completo de la respuesta de MP
        preference_response = payment_service.create_event_preference(
            purchase=purchase,
            items=mp_items,
            buyer_email=current_user.email
        )
        print("preference response:", preference_response)
        return CreatePreferenceResponse(
            purchaseId=str(purchase.id),
            initPoint=preference_response["init_point"], # URL para redirigir
            preferenceId=preference_response["id"]
        )

    except Exception as e:
        logger.error(f"Error creando preferencia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la solicitud de pago: {str(e)}"
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
        print(f"🔔 Webhook recibido: {body}")
        
        topic = body.get("topic")
        action = body.get("action")
        
        # Solo procesar notificaciones de pago
        if topic == "payment" or action == "payment.created":
            payment_id = body.get("resource")
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
