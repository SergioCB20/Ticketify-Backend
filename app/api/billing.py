"""
API Endpoints para el Sistema de Facturación de Organizadores
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.billing_service import BillingService
from app.schemas.billing import (
    OrganizerEventBillingSchema,
    EventBillingDetailSchema,
    BillingSyncResponseSchema
)

router = APIRouter(prefix="/organizer/billing", tags=["Billing - Organizador"])


# ============================================================
# Verificación de Rol
# ============================================================

def verify_organizer_role(current_user: User = Depends(get_current_active_user)):
    """Verificar que el usuario sea organizador"""
    if not any(role.name == "ORGANIZER" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los organizadores pueden acceder a esta funcionalidad"
        )
    return current_user


# ============================================================
# Endpoints
# ============================================================

@router.get("/events", response_model=List[OrganizerEventBillingSchema])
async def get_organizer_events(
    current_user: User = Depends(verify_organizer_role),
    db: Session = Depends(get_db)
):
    """
    📊 **Obtener lista de eventos con datos de facturación**
    
    Retorna todos los eventos del organizador con información resumida de:
    - Ingresos totales
    - Cantidad de transacciones
    - Monto neto (después de comisiones)
    - Estado del evento
    
    **Requiere:**
    - Usuario autenticado
    - Rol: ORGANIZER
    
    **Retorna:**
    Lista de eventos con datos de facturación
    """
    billing_service = BillingService(db)
    
    try:
        events = billing_service.get_organizer_events(current_user.id)
        return events
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener los eventos: {str(e)}"
        )


@router.get("/events/{event_id}", response_model=EventBillingDetailSchema)
async def get_event_billing_detail(
    event_id: str,
    current_user: User = Depends(verify_organizer_role),
    db: Session = Depends(get_db)
):
    """
    📈 **Obtener detalle completo de facturación de un evento**
    
    Retorna información detallada incluyendo:
    - **Resumen financiero**: Ingresos, comisiones, monto neto
    - **Acreditación**: Fondos acreditados y pendientes
    - **Métodos de pago**: Distribución y porcentajes
    - **Transacciones**: Lista completa con detalles
    - **Última sincronización**: Timestamp de última actualización
    
    **Parámetros:**
    - `event_id`: UUID del evento
    
    **Requiere:**
    - Usuario autenticado
    - Rol: ORGANIZER
    - Ser propietario del evento
    
    **Errores:**
    - 404: Evento no encontrado o sin permisos
    - 500: Error interno del servidor
    """
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de evento inválido"
        )
    
    billing_service = BillingService(db)
    
    try:
        detail = billing_service.get_event_billing_detail(event_uuid, current_user.id)
        return detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el detalle del evento: {str(e)}"
        )


@router.post("/events/{event_id}/sync", response_model=BillingSyncResponseSchema)
async def sync_event_billing(
    event_id: str,
    current_user: User = Depends(verify_organizer_role),
    db: Session = Depends(get_db)
):
    """
    🔄 **Sincronizar datos de facturación con MercadoPago**
    
    Actualiza el estado de todas las transacciones del evento consultando
    directamente a la API de MercadoPago.
    
    **Proceso:**
    1. Verifica que tengas una cuenta de MercadoPago vinculada
    2. Consulta el estado de cada transacción en MercadoPago
    3. Actualiza la información en la base de datos
    4. Retorna el número de transacciones actualizadas
    
    **Parámetros:**
    - `event_id`: UUID del evento
    
    **Requiere:**
    - Usuario autenticado
    - Rol: ORGANIZER
    - Cuenta de MercadoPago vinculada
    - Ser propietario del evento
    
    **Retorna:**
    - Mensaje de resultado
    - Cantidad de transacciones actualizadas
    - Timestamp de la sincronización
    
    **Errores:**
    - 400: Cuenta de MercadoPago no vinculada
    - 404: Evento no encontrado
    - 500: Error en la sincronización
    """
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de evento inválido"
        )
    
    billing_service = BillingService(db)
    
    try:
        result = billing_service.sync_event_billing(event_uuid, current_user.id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al sincronizar los datos: {str(e)}"
        )


@router.get("/events/{event_id}/report")
async def download_billing_report(
    event_id: str,
    format: str = Query(..., description="Formato del reporte (pdf o excel)", regex="^(pdf|excel)$"),
    current_user: User = Depends(verify_organizer_role),
    db: Session = Depends(get_db)
):
    """
    📥 **Descargar reporte de facturación**
    
    Genera y descarga un reporte detallado de facturación en formato PDF o Excel.
    
    **El reporte incluye:**
    - Información del evento
    - Resumen financiero completo
    - Desglose de comisiones
    - Distribución de métodos de pago
    - Lista completa de transacciones
    
    **Parámetros:**
    - `event_id`: UUID del evento
    - `format`: Formato del reporte
      - `pdf`: Documento PDF formateado
      - `excel`: Hoja de cálculo XLSX
    
    **Requiere:**
    - Usuario autenticado
    - Rol: ORGANIZER
    - Ser propietario del evento
    
    **Retorna:**
    Archivo binario (PDF o Excel) para descarga
    
    **Errores:**
    - 400: Formato inválido o ID inválido
    - 404: Evento no encontrado
    - 500: Error generando el reporte
    
    **Ejemplo de uso:**
    ```
    GET /api/organizer/billing/events/{event_id}/report?format=pdf
    GET /api/organizer/billing/events/{event_id}/report?format=excel
    ```
    """
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de evento inválido"
        )
    
    billing_service = BillingService(db)
    
    try:
        # Verificar que el usuario tenga acceso al evento
        detail = billing_service.get_event_billing_detail(event_uuid, current_user.id)
        
        # Generar el reporte según el formato
        if format == "pdf":
            report_data = billing_service.generate_pdf_report(event_uuid, current_user.id)
            media_type = "application/pdf"
            filename = f"facturacion_{detail.eventName.replace(' ', '_')}_{event_id[:8]}.pdf"
        else:  # excel
            report_data = billing_service.generate_excel_report(event_uuid, current_user.id)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"facturacion_{detail.eventName.replace(' ', '_')}_{event_id[:8]}.xlsx"
        
        # Crear stream de bytes
        report_stream = io.BytesIO(report_data)
        
        # Retornar como descarga
        return StreamingResponse(
            report_stream,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el reporte: {str(e)}"
        )


# ============================================================
# Endpoint de Estado (Opcional - Para debugging)
# ============================================================

@router.get("/status")
async def get_billing_status(
    current_user: User = Depends(verify_organizer_role),
    db: Session = Depends(get_db)
):
    """
    🔍 **Verificar estado del sistema de facturación**
    
    Endpoint de utilidad para verificar:
    - Conexión a MercadoPago
    - Cantidad de eventos del organizador
    - Estado general del sistema
    
    **Requiere:**
    - Usuario autenticado
    - Rol: ORGANIZER
    
    **Retorna:**
    Información de estado del sistema de facturación
    """
    billing_service = BillingService(db)
    
    try:
        events = billing_service.get_organizer_events(current_user.id)
        
        return {
            "status": "operational",
            "organizerId": str(current_user.id),
            "organizerEmail": current_user.email,
            "mercadopagoConnected": current_user.isMercadopagoConnected,
            "mercadopagoEmail": current_user.mercadopagoEmail if current_user.isMercadopagoConnected else None,
            "totalEvents": len(events),
            "hasEvents": len(events) > 0
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
