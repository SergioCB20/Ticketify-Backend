from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException, status
from pydantic import ValidationError
from datetime import datetime
import uuid

from app.repositories.event_repository import EventRepository
from app.schemas.event import (
    EventCreate, 
    EventUpdate, 
    EventDetailResponse,
    EventResponse, 
    OrganizerEventResponse,
    EventSearchResponse
)
from app.models.event import Event, EventStatus
from app.models.event_category import EventCategory


class EventService:
    """Event service with business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)
    
    def get_event_by_id(self, event_id: str) -> EventResponse:
        """Get a single event by ID, including ticket types."""
        event = self.event_repo.get_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        print(f"🟢 EVENTO ENCONTRADO: {event.title}")
        if hasattr(event, "ticket_types"):
            print(f"🎟️ Ticket types encontrados: {len(event.ticket_types)}")
            for tt in event.ticket_types:
                print(f"➡️ {tt.name} | precio: {tt.price} | activo: {tt.is_active}")

        # ✅ Convertimos manualmente el modelo SQLAlchemy a dict
        event_dict = event.to_dict()

        # ✅ Retornamos un modelo Pydantic EventDetailResponse
        return EventDetailResponse(**event_dict)

    
    def get_all_events(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        status_filter: Optional[str] = None
    ) -> List[EventResponse]:
        """Get all events with pagination"""
        event_status = None
        if status_filter:
            try:
                event_status = EventStatus[status_filter.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado inválido: {status_filter}"
                )
        else:
            event_status = EventStatus.PUBLISHED
        
        events = self.event_repo.get_all(skip=skip, limit=limit, status=event_status)
        
        # Enrich all events with additional data and validate via EventResponse
        try:
            event_responses = [
                EventResponse(**(event.to_dict() if hasattr(event, 'to_dict') else {}))
                for event in events
            ]
        except ValidationError as e:
            # Raise HTTP 500 with validation details for easier debugging
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al validar datos del evento: {e}"
            )

        return event_responses
    def get_active_events(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        status_filter: Optional[str] = None
    ) -> List[EventResponse]:
        """Get all future or active events with pagination"""
        event_status = None
        if status_filter:
            try:
                event_status = EventStatus[status_filter.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado inválido: {status_filter}"
                )
        else:
            event_status = EventStatus.PUBLISHED

        # Llamada al repositorio
        events = self.event_repo.get_all(skip=skip, limit=limit, status=event_status)

        # 🔥 FILTRO DE FECHA AQUÍ (solo eventos cuyo fin aún no pasó)
        now = datetime.now(timezone.utc)
        upcoming_events = [
            e for e in events
            if getattr(e, "endDate", None) and e.endDate > now
        ]

        # Enrich all events with additional data and validate via EventResponse
        try:
            event_responses = [
                EventResponse(**(event.to_dict() if hasattr(event, 'to_dict') else {}))
                for event in upcoming_events
            ]
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al validar datos del evento: {e}"
            )

        return event_responses
    
    
    def search_events(
        self,
        query: Optional[str] = None,
        categories: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        location: Optional[str] = None,
        venue: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> EventSearchResponse:
        """
        Search events with multiple filters
        """
        # Parse status
        event_status = None
        if status_filter:
            try:
                event_status = EventStatus[status_filter.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Estado inválido: {status_filter}"
                )
        else:
            event_status = EventStatus.PUBLISHED
        
        # Parse categories
        category_ids = None
        if categories:
            category_list = [c.strip() for c in categories.split(',') if c.strip()]
            if category_list:
                # Get category IDs from slugs
                category_records = self.db.query(EventCategory).filter(
                    EventCategory.slug.in_(category_list),
                    EventCategory.is_active == True
                ).all()
                
                if category_records:
                    category_ids = [cat.id for cat in category_records]
                else:
                    # No valid categories found
                    return EventSearchResponse(
                        events=[],
                        total=0,
                        page=page,
                        page_size=page_size,
                        total_pages=0
                    )
        
        # Parse dates
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha de inicio inválido. Use YYYY-MM-DD"
                )
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de fecha de fin inválido. Use YYYY-MM-DD"
                )
        
        # Search events
        events, total_count = self.event_repo.get_events(
            query=query,
            category_ids=category_ids,
            min_price=min_price,
            max_price=max_price,
            start_date=start_datetime,
            end_date=end_datetime,
            location=location,
            venue=venue,
            status=event_status,
            page=page,
            page_size=page_size
        )
        
        # Enrich events with additional data
        event_responses = []
        for event in events:
            event_dict = event.to_dict() if hasattr(event, 'to_dict') else {}
            event_responses.append(event_dict)
        
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size
        
        return EventSearchResponse(
            events=event_responses,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def create_event(self, event_data: EventCreate, organizer_id: uuid.UUID) -> EventResponse:
        """Create a new event"""
        # Validate category
        if event_data.category_id:
            category = self.db.query(EventCategory).filter(
                EventCategory.id == event_data.category_id,
                EventCategory.is_active == True
            ).first()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada o inactiva"
                )
        
        # Validate dates
        if event_data.endDate <= event_data.startDate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin debe ser posterior a la fecha de inicio"
            )
        
        if event_data.startDate < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio no puede ser en el pasado"
            )
        
        # Create event
        event = self.event_repo.create_event(event_data, organizer_id)

        event_dict = event.to_dict() if hasattr(event, 'to_dict') else {}
        return EventResponse(**event_dict)
    
    def update_event(
        self, 
        event_id: str, 
        event_data: EventUpdate, 
        user_id: uuid.UUID
    ) -> EventResponse:
        """Update an event (only by organizer)"""
        event = self.event_repo.get_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Verify organizer
        if str(event.organizer_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar este evento"
            )
        
        # Validate category if updating
        if event_data.category_id:
            category = self.db.query(EventCategory).filter(
                EventCategory.id == event_data.category_id,
                EventCategory.is_active == True
            ).first()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada o inactiva"
                )
        
        # Validate dates if updating
        if event_data.startDate and event_data.endDate:
            if event_data.endDate <= event_data.startDate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de fin debe ser posterior a la fecha de inicio"
                )
        
        # Update event
        updated_event = self.event_repo.update_event(event_id, event_data)

        if not updated_event:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el evento"
            )
        
        event_dict = updated_event.to_dict() if hasattr(updated_event, 'to_dict') else {}
        return EventResponse(**event_dict)
    
    def delete_event(self, event_id: str, user_id: uuid.UUID) -> Dict[str, str]:
        """Delete an event (only by organizer)"""
        event = self.event_repo.get_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Verify organizer
        if str(event.organizer_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para eliminar este evento"
            )
        
        # Check if tickets have been sold
        tickets_sold = self.event_repo.get_tickets_sold(event_id)
        if tickets_sold > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un evento con tickets vendidos"
            )
        
        # Delete event
        success = self.event_repo.delete(event_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el evento"
            )
        
        return {"message": "Evento eliminado exitosamente"}
    
    def publish_event(self, event_id: str, user_id: uuid.UUID) -> EventResponse:
        """Publish an event (change from DRAFT to PUBLISHED)"""
        event = self.event_repo.get_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Verify organizer
        if str(event.organizer_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para publicar este evento"
            )
        
        # Validate event has tickets
        if not event.ticket_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El evento debe tener al menos un tipo de ticket antes de publicarse"
            )
        
        # Publish event
        published_event = self.event_repo.publish_event(event_id)

        if not published_event:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al publicar el evento"
            )
        
        event_dict = published_event.to_dict() if hasattr(published_event, 'to_dict') else {}
        return EventResponse(**event_dict)
    
    def cancel_event(self, event_id: str, user_id: uuid.UUID) -> EventResponse:
        """Cancel an event"""
        event = self.event_repo.get_by_id(event_id)
        
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Verify organizer
        if str(event.organizer_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cancelar este evento"
            )
        
        # Cancel event
        cancelled_event = self.event_repo.cancel_event(event_id)

        if not cancelled_event:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al cancelar el evento"
            )
        
        event_dict = cancelled_event.to_dict() if hasattr(cancelled_event, 'to_dict') else {}
        return EventResponse(**event_dict)

    def set_draft_event(self, event_id: str, user_id: uuid.UUID) -> EventResponse:
        """Set an event status to DRAFT (only by organizer)."""
        event = self.event_repo.get_by_id(event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        # Verify organizer
        if str(event.organizer_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cambiar el estado de este evento"
            )

        # Set draft
        drafted_event = self.event_repo.set_draft_event(event_id)

        if not drafted_event:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al poner el evento en DRAFT"
            )

        event_dict = drafted_event.to_dict() if hasattr(drafted_event, 'to_dict') else {}
        return EventResponse(**event_dict)

    def complete_event(self, event_id: str, user_id: uuid.UUID) -> EventResponse:
        """Mark an event as COMPLETED (only by organizer)."""
        event = self.event_repo.get_by_id(event_id)

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        # Verify organizer
        if str(event.organizer_id) != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cambiar el estado de este evento"
            )

        # Optionally: you might check that event.startDate < now() or other business rules

        completed_event = self.event_repo.complete_event(event_id)

        if not completed_event:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al marcar el evento como COMPLETED"
            )

        event_dict = completed_event.to_dict() if hasattr(completed_event, 'to_dict') else {}
        return EventResponse(**event_dict)
    
    def get_featured_events(self, limit: int = 6) -> List[EventResponse]:
        """Get featured events (upcoming published events)"""
        events = self.event_repo.get_featured_events(limit=limit)
        # Enrich all events and validate
        try:
            event_responses = [
                EventResponse(**(event.to_dict() if hasattr(event, 'to_dict') else {}))
                for event in events
            ]
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al validar datos del evento destacado: {e}"
            )

        return event_responses
    
    def get_organizer_events(
        self,
        organizer_id: uuid.UUID,
    ) -> List[OrganizerEventResponse]:
        """Get events by organizer and return simplified organizer view."""
        events = self.event_repo.get_events_by_organizer_id(organizer_id)

        try:
            organizer_events: List[OrganizerEventResponse] = []
            for event in events:
                total_capacity = getattr(event, "totalCapacity", None)
                available = getattr(event, "available_tickets", None)
                sold = None
                if total_capacity is not None and available is not None:
                    try:
                        sold = int(total_capacity) - int(available)
                    except Exception:
                        sold = None

                ev = {
                    "id": event.id,
                    "title": event.title,
                    "date": getattr(event, "startDate", None),
                    "location": getattr(event, "venue", None),
                    "totalTickets": total_capacity,
                    "soldTickets": sold,
                    "status": event.status.value if hasattr(event.status, "value") else event.status,
                    "imageUrl": (event.multimedia[0] if getattr(event, "multimedia", None) and len(event.multimedia) > 0 else None)
                }

                organizer_events.append(OrganizerEventResponse(**ev))
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al validar datos de eventos del organizador: {e}"
            )

        return organizer_events
    