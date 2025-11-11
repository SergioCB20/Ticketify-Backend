from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventListResponse
from app.models.event import Event, EventStatus


class EventService:
    """Service layer for event business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)
    
    def create_event(self, event_data: EventCreate, organizer_id: UUID) -> EventResponse:
        """Create a new event"""
        # Validate dates
        if event_data.endDate <= event_data.startDate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin debe ser posterior a la fecha de inicio"
            )
        
        # Validate start date is in the future
        if event_data.startDate <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio debe ser en el futuro"
            )
        
        # Create event
        event = self.event_repo.create_event(event_data, organizer_id)
        
        return self._event_to_response(event)
    
    def get_event(self, event_id: UUID) -> EventResponse:
        """Get event by ID"""
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        return self._event_to_response(event)
    
    def get_events(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        category_id: Optional[UUID] = None,
        organizer_id: Optional[UUID] = None,
        search: Optional[str] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None
    ) -> EventListResponse:
        """Get list of events with filters and pagination"""
        # Validate page and page_size
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        skip = (page - 1) * page_size
        
        # Convert status string to enum if provided
        status_enum = None
        if status:
            try:
                status_enum = EventStatus[status.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado inválido: {status}"
                )
        
        # Get events from repository
        events, total = self.event_repo.get_events(
            skip=skip,
            limit=page_size,
            status=status_enum,
            category_id=category_id,
            organizer_id=organizer_id,
            search=search,
            start_date_from=start_date_from,
            start_date_to=start_date_to
        )
        
        # Convert to response models
        event_responses = [self._event_to_response(event) for event in events]
        
        total_pages = (total + page_size - 1) // page_size
        
        return EventListResponse(
            events=event_responses,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    def update_event(
        self, 
        event_id: UUID, 
        event_data: EventUpdate, 
        user_id: UUID,
        is_admin: bool = False
    ) -> EventResponse:
        """Update event (only by organizer or admin)"""
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Check permissions
        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para editar este evento"
            )
        
        # Validate dates if provided
        if event_data.startDate and event_data.endDate:
            if event_data.endDate <= event_data.startDate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de fin debe ser posterior a la fecha de inicio"
                )
        
        # Update event
        updated_event = self.event_repo.update_event(event_id, event_data)
        
        return self._event_to_response(updated_event)
    
    def delete_event(self, event_id: UUID, user_id: UUID, is_admin: bool = False) -> dict:
        """Delete event (only by organizer or admin)"""
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Check permissions
        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este evento"
            )
        
        # Check if event has sold tickets
        if event.available_tickets < event.totalCapacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un evento que ya tiene tickets vendidos"
            )
        
        success = self.event_repo.delete_event(event_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al eliminar el evento"
            )
        
        return {"message": "Evento eliminado exitosamente", "success": True}
    
    def update_event_status(
        self, 
        event_id: UUID, 
        new_status: str,
        user_id: UUID,
        is_admin: bool = False
    ) -> EventResponse:
        """Update event status"""
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Check permissions
        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cambiar el estado de este evento"
            )
        
        # Validate status
        try:
            status_enum = EventStatus[new_status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido: {new_status}"
            )
        
        # Update status
        updated_event = self.event_repo.update_event_status(event_id, status_enum)
        
        return self._event_to_response(updated_event)
    
    def get_my_events(self, organizer_id: UUID, page: int = 1, page_size: int = 10) -> EventListResponse:
        """Get events created by the current user"""
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        skip = (page - 1) * page_size
        
        events, total = self.event_repo.get_events_by_organizer(
            organizer_id=organizer_id,
            skip=skip,
            limit=page_size
        )
        
        event_responses = [self._event_to_response(event) for event in events]
        total_pages = (total + page_size - 1) // page_size
        
        return EventListResponse(
            events=event_responses,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    def get_upcoming_events(self, page: int = 1, page_size: int = 10) -> EventListResponse:
        """Get upcoming published events"""
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        skip = (page - 1) * page_size
        
        events, total = self.event_repo.get_upcoming_events(skip=skip, limit=page_size)
        
        event_responses = [self._event_to_response(event) for event in events]
        total_pages = (total + page_size - 1) // page_size
        
        return EventListResponse(
            events=event_responses,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    def get_featured_events(self, limit: int = 6) -> List[EventResponse]:
        """Get featured events"""
        events = self.event_repo.get_featured_events(limit=limit)
        return [self._event_to_response(event) for event in events]
    
    def search_events(self, search_term: str, page: int = 1, page_size: int = 10) -> EventListResponse:
        """Search events"""
        if not search_term or len(search_term) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El término de búsqueda debe tener al menos 2 caracteres"
            )
        
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        skip = (page - 1) * page_size
        
        events, total = self.event_repo.search_events(
            search_term=search_term,
            skip=skip,
            limit=page_size
        )
        
        event_responses = [self._event_to_response(event) for event in events]
        total_pages = (total + page_size - 1) // page_size
        
        return EventListResponse(
            events=event_responses,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    def _event_to_response(self, event: Event) -> EventResponse:
        """Convert Event model to EventResponse"""
        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            startDate=event.startDate,
            endDate=event.endDate,
            venue=event.venue,
            totalCapacity=event.totalCapacity,
            status=event.status.value,
            multimedia=event.multimedia if event.multimedia else [],
            availableTickets=event.available_tickets,
            isSoldOut=event.is_sold_out,
            organizerId=event.organizer_id,
            categoryId=event.category_id,
            createdAt=event.createdAt,
            updatedAt=event.updatedAt
        )
