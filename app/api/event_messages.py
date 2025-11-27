"""
API endpoints para mensajes a asistentes de eventos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.event_message import (
    EventMessageCreate,
    EventMessageResponse,
    EventAttendeeResponse,
    MessageStatsResponse
)
from app.services.event_message_service import EventMessageService


router = APIRouter()


@router.post(
    "/{event_id}/messages",
    response_model=EventMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar mensaje a asistentes",
    description="Permite al organizador enviar un mensaje a todos los asistentes de un evento"
)
def send_message_to_attendees(
    event_id: UUID,
    message_data: EventMessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enviar un mensaje a los asistentes de un evento.
    
    **Requiere autenticación y ser el organizador del evento.**
    
    - **event_id**: ID del evento
    - **subject**: Asunto del mensaje (máx 200 caracteres)
    - **content**: Contenido HTML del mensaje (máx 5000 caracteres)
    - **message_type**: BROADCAST (todos), FILTERED (con filtros), INDIVIDUAL
    - **recipient_filters**: Filtros opcionales en formato JSON
    """
    service = EventMessageService(db)
    
    # Validar que el usuario es el organizador del evento
    if not service.validate_organizer_access(event_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para enviar mensajes en este evento"
        )
    
    try:
        message = service.send_message_to_attendees(
            event_id=event_id,
            organizer_id=current_user.id,
            message_data=message_data
        )
        
        return message.to_dict()
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar mensaje: {str(e)}"
        )


@router.get(
    "/{event_id}/messages",
    summary="Obtener mensajes enviados",
    description="Obtiene el historial de mensajes enviados a asistentes de un evento"
)
def get_event_messages(
    event_id: UUID,
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(20, ge=1, le=100, description="Mensajes por página"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de mensajes enviados.
    
    **Requiere autenticación y ser el organizador del evento.**
    
    Retorna una lista paginada de mensajes con sus estadísticas.
    """
    service = EventMessageService(db)
    
    # Validar acceso
    if not service.validate_organizer_access(event_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver mensajes de este evento"
        )
    
    try:
        result = service.get_event_messages(event_id, page, limit)
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener mensajes: {str(e)}"
        )


@router.get(
    "/{event_id}/messages/{message_id}",
    response_model=EventMessageResponse,
    summary="Obtener detalles de un mensaje",
    description="Obtiene información detallada de un mensaje específico"
)
def get_message_details(
    event_id: UUID,
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener detalles completos de un mensaje.
    
    **Requiere autenticación y ser el organizador del evento.**
    """
    service = EventMessageService(db)
    
    # Validar acceso
    if not service.validate_organizer_access(event_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este mensaje"
        )
    
    message = service.get_message_by_id(event_id, message_id)
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado"
        )
    
    return message.to_dict()


@router.get(
    "/{event_id}/attendees",
    response_model=List[EventAttendeeResponse],
    summary="Obtener lista de asistentes",
    description="Obtiene la lista de asistentes del evento para preview antes de enviar mensajes"
)
def get_event_attendees(
    event_id: UUID,
    ticket_type_id: Optional[UUID] = Query(None, description="Filtrar por tipo de ticket"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de asistentes del evento.
    
    **Requiere autenticación y ser el organizador del evento.**
    
    Útil para previsualizar cuántos asistentes recibirán el mensaje.
    """
    service = EventMessageService(db)
    
    # Validar acceso
    if not service.validate_organizer_access(event_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver asistentes de este evento"
        )
    
    try:
        attendees = service.get_event_attendees(event_id, ticket_type_id)
        return attendees
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asistentes: {str(e)}"
        )


@router.get(
    "/{event_id}/messages/stats",
    response_model=MessageStatsResponse,
    summary="Obtener estadísticas de mensajes",
    description="Obtiene estadísticas generales de mensajes del evento"
)
def get_message_stats(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas de mensajes del evento.
    
    **Requiere autenticación y ser el organizador del evento.**
    
    Incluye: total de mensajes, destinatarios, tasa de éxito promedio, etc.
    """
    service = EventMessageService(db)
    
    # Validar acceso
    if not service.validate_organizer_access(event_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estadísticas de este evento"
        )
    
    try:
        stats = service.get_message_stats(event_id)
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
