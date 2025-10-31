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


@router.get("/", response_model=EventListResponse)
async def get_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status (DRAFT, PUBLISHED, CANCELLED, COMPLETED)"),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    organizer_id: Optional[UUID] = Query(None, description="Filter by organizer ID"),
    search: Optional[str] = Query(None, description="Search in title, description, venue"),
    start_date_from: Optional[datetime] = Query(None, description="Filter events starting from this date"),
    start_date_to: Optional[datetime] = Query(None, description="Filter events starting until this date"),
    db: Session = Depends(get_db)
):
    """
    Get list of events with filters and pagination
    
    Returns paginated list of events with total count
    """
    event_service = EventService(db)
    return event_service.get_events(
        page=page,
        page_size=page_size,
        status=status,
        category_id=category_id,
        organizer_id=organizer_id,
        search=search,
        start_date_from=start_date_from,
        start_date_to=start_date_to
    )


@router.get("/upcoming", response_model=EventListResponse)
async def get_upcoming_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get upcoming published events
    
    Returns events that are published and have a start date in the future
    """
    event_service = EventService(db)
    return event_service.get_upcoming_events(page=page, page_size=page_size)


@router.get("/featured", response_model=List[EventResponse])
async def get_featured_events(
    limit: int = Query(6, ge=1, le=20, description="Number of featured events"),
    db: Session = Depends(get_db)
):
    """
    Get featured events
    
    Returns a limited list of featured events (published, upcoming, with available tickets)
    """
    event_service = EventService(db)
    return event_service.get_featured_events(limit=limit)


@router.get("/my-events", response_model=EventListResponse)
async def get_my_events(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get events created by the current user
    
    Returns all events where the current user is the organizer
    """
    event_service = EventService(db)
    return event_service.get_my_events(
        organizer_id=current_user.id,
        page=page,
        page_size=page_size
    )


@router.get("/search", response_model=EventListResponse)
async def search_events(
    q: str = Query(..., min_length=2, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Search events by title, description, or venue
    
    Returns events that match the search term (minimum 2 characters)
    """
    event_service = EventService(db)
    return event_service.search_events(
        search_term=q,
        page=page,
        page_size=page_size
    )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get event by ID
    
    Returns detailed information about a specific event
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
