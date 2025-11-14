from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.event_service import EventService
from app.schemas.event import (
    EventCreate, EventUpdate, EventResponse, EventListResponse,
    MessageResponse, EventStatusUpdate
)
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new event
    
    - **title**: Event title (3-200 characters)
    - **description**: Event description (optional)
    - **startDate**: Event start date and time (must be in the future)
    - **endDate**: Event end date and time (must be after startDate)
    - **venue**: Event location/venue (3-200 characters)
    - **totalCapacity**: Total capacity (must be > 0)
    - **multimedia**: List of image/video URLs (optional)
    - **category_id**: Event category UUID (optional)
    
    Returns the created event with status DRAFT
    """
    event_service = EventService(db)
    return event_service.create_event(event_data, current_user.id)


@router.get("/{event_id}/photo")
async def get_event_photo(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Obtener la foto de un evento.
    """
    event_service = EventService(db)
    return event_service.get_event(event_id)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update event
    
    Only the event organizer or an admin can update the event.
    Only provided fields will be updated.
    """
    event_service = EventService(db)
    
    # Check if user is admin
    is_admin = any(role.name == "ADMIN" for role in current_user.roles) if current_user.roles else False
    
    return event_service.update_event(
        event_id=event_id,
        event_data=event_data,
        user_id=current_user.id,
        is_admin=is_admin
    )


@router.patch("/{event_id}/status", response_model=EventResponse)
async def update_event_status(
    event_id: UUID,
    status_data: EventStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update event status
    
    Possible statuses: DRAFT, PUBLISHED, CANCELLED, COMPLETED
    Only the event organizer or an admin can update the status.
    """
    event_service = EventService(db)
    
    # Check if user is admin
    is_admin = any(role.name == "ADMIN" for role in current_user.roles) if current_user.roles else False
    
    return event_service.update_event_status(
        event_id=event_id,
        new_status=status_data.status,
        user_id=current_user.id,
        is_admin=is_admin
    )


@router.delete("/{event_id}", response_model=MessageResponse)
async def delete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete event
    
    Only the event organizer or an admin can delete the event.
    Cannot delete events that have sold tickets.
    """
    event_service = EventService(db)
    
    # Check if user is admin
    is_admin = any(role.name == "ADMIN" for role in current_user.roles) if current_user.roles else False
    
    return event_service.delete_event(
        event_id=event_id,
        user_id=current_user.id,
        is_admin=is_admin
    )
