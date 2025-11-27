"""
Webhooks de MercadoPago para actualizaciones automáticas de pagos
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
import mercadopago
import hashlib
import hmac
import logging

from app.core.database import get_db
from app.core.config import settings
from app.models.purchase import Purchase, PurchaseStatus
from app.models.payment import Payment, PaymentStatus
from app.models.user import User
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# ============================================================
# Verificación de Firma
# ============================================================

def verify_mercadopago_signature(
    x_signature: str,
    x_request_id: str,
    data_id: str,
    secret: str
) -> bool:
    """
    Verificar la firma de un webhook de MercadoPago
    
    MercadoPago envía la firma en el header 'x-signature'
    Formato: ts=<timestamp>,v1=<hash>
    """
    try:
        # Parsear la firma
        parts = dict(item.split('=') for item in x_signature.split(','))
        ts = parts.get('ts')
        v1 = parts.get('v1')
        
        if not ts or not v1:
            logger.error("Firma inválida: falta ts o v1")
            return False
        
        # Construir el string para verificar
        # Formato: id + request_id + ts
        manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
        
        # Calcular HMAC
        hmac_obj = hmac.new(
            secret.encode(),
            manifest.encode(),
            hashlib.sha256
        )
        calculated_signature = hmac_obj.hexdigest()
        
        # Comparar
        return hmac.compare_digest(calculated_signature, v1)
        
    except Exception as e:
        logger.error(f"Error al verificar firma: {str(e)}")
        return False


# ============================================================
# Webhook de Pagos
# ============================================================

@router.post("/mercadopago")
async def mercadopago_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_signature: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None)
):
    """
    🔔 **Webhook de MercadoPago**
    
    Recibe notificaciones automáticas cuando cambia el estado de un pago.
    
    **Tipos de notificaciones:**
    - `payment`: Cambio en estado de pago
    - `merchant_order`: Cambio en orden del vendedor
    
    **Eventos soportados:**
    - `payment.created`: Pago creado
    - `payment.updated`: Pago actualizado (aprobado, rechazado, etc.)
    
    **Configuración en MercadoPago:**
    1. Ir a: https://www.mercadopago.com/developers/panel/webhooks
    2. Agregar URL: `https://tu-dominio.com/api/webhooks/mercadopago`
    3. Seleccionar eventos: Payment
    
    **Seguridad:**
    - Verificación de firma HMAC-SHA256
    - Validación de source IP (opcional)
    - Validación de datos
    """
    try:
        # Obtener el body del request
        body = await request.json()
        
        logger.info(f"Webhook recibido: {body}")
        
        # Extraer información
        topic = body.get('type')  # Ej: 'payment'
        data = body.get('data', {})
        data_id = data.get('id')  # ID del pago
        
        if not topic or not data_id:
            logger.warning("Webhook inválido: falta topic o data_id")
            return {"status": "ignored", "reason": "missing_data"}
        
        # Verificar firma (si está configurado)
        if hasattr(settings, 'MERCADOPAGO_WEBHOOK_SECRET') and settings.MERCADOPAGO_WEBHOOK_SECRET:
            if not x_signature or not x_request_id:
                raise HTTPException(
                    status_code=401,
                    detail="Falta firma de verificación"
                )
            
            is_valid = verify_mercadopago_signature(
                x_signature,
                x_request_id,
                str(data_id),
                settings.MERCADOPAGO_WEBHOOK_SECRET
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=401,
                    detail="Firma inválida"
                )
        
        # Procesar según el tipo
        if topic == 'payment':
            await process_payment_notification(data_id, db)
        elif topic == 'merchant_order':
            logger.info(f"Merchant order notification: {data_id} (no procesado)")
        else:
            logger.info(f"Tipo de notificación no soportado: {topic}")
        
        # Retornar 200 OK para confirmar recepción
        return {"status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}")
        # Retornar 200 para evitar reintentos innecesarios
        return {"status": "error", "message": str(e)}


# ============================================================
# Procesamiento de Notificaciones
# ============================================================

async def process_payment_notification(payment_id: str, db: Session):
    """
    Procesar notificación de cambio en pago
    """
    try:
        logger.info(f"Procesando notificación de pago: {payment_id}")
        
        # Buscar la compra asociada al pago
        purchase = db.query(Purchase).filter(
            Purchase.payment_reference == str(payment_id)
        ).first()
        
        if not purchase:
            logger.warning(f"No se encontró compra para pago {payment_id}")
            return
        
        # Obtener el organizador del evento para usar su token
        event = purchase.event
        organizer = db.query(User).filter(User.id == event.organizer_id).first()
        
        if not organizer or not organizer.mercadopagoAccessToken:
            logger.error(f"Organizador sin token de MP para evento {event.id}")
            return
        
        # Inicializar SDK de MercadoPago con token del organizador
        mp_sdk = mercadopago.SDK(organizer.mercadopagoAccessToken)
        
        # Consultar el estado del pago
        payment_response = mp_sdk.payment().get(payment_id)
        
        if payment_response["status"] != 200:
            logger.error(f"Error al consultar pago en MP: {payment_response}")
            return
        
        payment_data = payment_response["response"]
        
        # Actualizar el estado de la compra
        old_status = purchase.status
        new_status = map_mercadopago_status(payment_data.get('status'))
        
        if old_status != new_status:
            purchase.status = new_status
            
            # Actualizar el pago asociado si existe
            if purchase.payment:
                purchase.payment.status = map_mercadopago_payment_status(payment_data.get('status'))
            
            # Actualizar fecha de pago si fue aprobado
            if new_status == PurchaseStatus.COMPLETED and payment_data.get('date_approved'):
                from datetime import datetime
                purchase.payment_date = datetime.fromisoformat(
                    payment_data['date_approved'].replace('Z', '+00:00')
                )
            
            db.commit()
            
            logger.info(
                f"✅ Compra {purchase.id} actualizada: {old_status} -> {new_status}"
            )
            
            # TODO: Enviar notificación por email al comprador
            # TODO: Enviar notificación al organizador si es relevante
        else:
            logger.info(f"Estado sin cambios para compra {purchase.id}: {old_status}")
        
    except Exception as e:
        logger.error(f"Error procesando notificación de pago: {str(e)}")
        db.rollback()
        raise


# ============================================================
# Mapeo de Estados
# ============================================================

def map_mercadopago_status(mp_status: str) -> PurchaseStatus:
    """Mapear estado de MercadoPago a estado de Purchase"""
    status_map = {
        'approved': PurchaseStatus.COMPLETED,
        'pending': PurchaseStatus.PENDING,
        'in_process': PurchaseStatus.PROCESSING,
        'rejected': PurchaseStatus.REJECTED,
        'refunded': PurchaseStatus.REFUNDED,
        'cancelled': PurchaseStatus.CANCELLED,
        'in_mediation': PurchaseStatus.PENDING,
        'charged_back': PurchaseStatus.REFUNDED
    }
    return status_map.get(mp_status, PurchaseStatus.PENDING)


def map_mercadopago_payment_status(mp_status: str) -> PaymentStatus:
    """Mapear estado de MercadoPago a estado de Payment"""
    status_map = {
        'approved': PaymentStatus.COMPLETED,
        'pending': PaymentStatus.PENDING,
        'in_process': PaymentStatus.PROCESSING,
        'rejected': PaymentStatus.FAILED,
        'refunded': PaymentStatus.REFUNDED,
        'cancelled': PaymentStatus.CANCELLED
    }
    return status_map.get(mp_status, PaymentStatus.PENDING)


# ============================================================
# Endpoint de Testing (solo desarrollo)
# ============================================================

@router.post("/mercadopago/test")
async def test_webhook(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    🧪 **Endpoint de prueba para simular webhook**
    
    Solo para desarrollo. Permite probar el procesamiento de webhooks manualmente.
    
    **Uso:**
    ```bash
    curl -X POST "http://localhost:8000/api/webhooks/mercadopago/test?payment_id=123456789"
    ```
    
    ⚠️ Desactivar en producción
    """
    if not settings.DEBUG:
        raise HTTPException(
            status_code=403,
            detail="Endpoint solo disponible en modo debug"
        )
    
    await process_payment_notification(payment_id, db)
    return {"status": "processed", "payment_id": payment_id}
