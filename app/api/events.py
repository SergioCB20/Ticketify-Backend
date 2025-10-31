from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models.event import Event, EventStatus
from app.models.user import User
from app.repositories.event_repository import EventRepository
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
    EventDetailResponse
)

router = APIRouter(prefix="/events", tags=["events"])

# ============= CREAR EVENTO =============

@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo evento.
    Solo usuarios autenticados pueden crear eventos.
    """
    try:
        event_repo = EventRepository(db)
        event = event_repo.create_event(
            organizer_id=current_user.id,
            **event_data.model_dump()
        )
        return EventResponse.from_orm(event)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating event: {str(e)}"
        )

# ============= OBTENER EVENTO POR ID =============

@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtener detalles de un evento específico.
    """
    try:
        event_repo = EventRepository(db)
        event = event_repo.get_event_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        return EventDetailResponse.from_orm(event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching event: {str(e)}"
        )

# ============= ACTUALIZAR EVENTO =============

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un evento existente.
    Solo el organizador del evento puede actualizarlo.
    """
    try:
        event_repo = EventRepository(db)
        event = event_repo.get_event_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Verificar que el usuario sea el organizador
        if str(event.organizer_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this event"
            )
        
        updated_event = event_repo.update_event(
            event_id=event_id,
            **event_data.model_dump(exclude_unset=True)
        )
        
        return EventResponse.from_orm(updated_event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating event: {str(e)}"
        )

# ============= ELIMINAR EVENTO =============

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un evento.
    Solo el organizador del evento puede eliminarlo.
    """
    try:
        event_repo = EventRepository(db)
        event = event_repo.get_event_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Verificar que el usuario sea el organizador
        if str(event.organizer_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this event"
            )
        
        event_repo.delete_event(event_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting event: {str(e)}"
        )

# ============= ACTUALIZAR ESTADO DEL EVENTO =============

@router.patch("/{event_id}/status", response_model=EventResponse)
async def update_event_status(
    event_id: UUID,
    new_status: EventStatus = Query(..., description="Nuevo estado del evento"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar el estado de un evento.
    Solo el organizador del evento puede cambiar su estado.
    """
    try:
        event_repo = EventRepository(db)
        event = event_repo.get_event_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        
        # Verificar que el usuario sea el organizador
        if str(event.organizer_id) != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this event's status"
            )
        
        updated_event = event_repo.update_event_status(event_id, new_status)
        
        return EventResponse.from_orm(updated_event)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating event status: {str(e)}"
        )

# ============= OBTENER EVENTOS (CON FILTROS) =============

@router.get("/", response_model=EventListResponse)
async def get_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[EventStatus] = None,
    category_id: Optional[UUID] = None,
    organizer_id: Optional[UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Obtener lista de eventos con filtros opcionales.
    Si se proporciona organizer_id, devuelve solo los eventos de ese organizador.
    """
    try:
        event_repo = EventRepository(db)
        
        # Si se proporciona organizer_id, usar método específico
        if organizer_id:
            events, total = event_repo.get_events_by_organizer(
                organizer_id=organizer_id,
                page=page,
                page_size=page_size
            )
        else:
            events, total = event_repo.get_events(
                page=page,
                page_size=page_size,
                search=search,
                status=status_filter,
                category_id=category_id
            )
        
        total_pages = (total + page_size - 1) // page_size
        
        return EventListResponse(
            events=[EventResponse.from_orm(event) for event in events],
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching events: {str(e)}"
        )
