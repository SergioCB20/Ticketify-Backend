from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime
import uuid

from app.models.event import Event, EventStatus
from app.models.event_category import EventCategory
from app.models.ticket_type import TicketType
from app.schemas.event import EventCreate, EventUpdate


class EventRepository:
    """Repository for Event database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        return self.db.query(Event).filter(Event.id == event_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 20, status: Optional[EventStatus] = None) -> List[Event]:
        """Get all events with pagination"""
        query = self.db.query(Event)
        
        if status:
            query = query.filter(Event.status == status)
        
        return query.order_by(Event.startDate.asc()).offset(skip).limit(limit).all()
    
    def get_by_organizer(self, organizer_id: uuid.UUID, skip: int = 0, limit: int = 20) -> List[Event]:
        """Get events by organizer"""
        return self.db.query(Event).filter(
            Event.organizer_id == organizer_id
        ).order_by(Event.startDate.desc()).offset(skip).limit(limit).all()
    
    def search(
        self,
        query: Optional[str] = None,
        category_ids: Optional[List[uuid.UUID]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        venue: Optional[str] = None,
        status: Optional[EventStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Event], int]:
        """
        Search events with multiple filters
        Returns: (events, total_count)
        """
        query_filters = []
        
        # Status filter
        if status:
            query_filters.append(Event.status == status)
        else:
            query_filters.append(Event.status == EventStatus.PUBLISHED)
        
        # Text search
        if query:
            text_filter = or_(
                Event.title.ilike(f"%{query}%"),
                Event.description.ilike(f"%{query}%")
            )
            query_filters.append(text_filter)
        
        # Category filter
        if category_ids:
            query_filters.append(Event.category_id.in_(category_ids))
        
        # Location filters
        if location:
            query_filters.append(Event.venue.ilike(f"%{location}%"))
        
        if venue:
            query_filters.append(Event.venue.ilike(f"%{venue}%"))
        
        # Date filters
        if start_date:
            query_filters.append(Event.startDate >= start_date)
        
        if end_date:
            end_datetime = end_date.replace(hour=23, minute=59, second=59)
            query_filters.append(Event.endDate <= end_datetime)
        
        # Build base query
        events_query = self.db.query(Event).filter(and_(*query_filters)) if query_filters else self.db.query(Event)
        
        # Price filter (requires join with ticket_types)
        if min_price is not None or max_price is not None:
            ticket_subquery = self.db.query(TicketType.event_id).distinct()
            
            if min_price is not None and max_price is not None:
                ticket_subquery = ticket_subquery.filter(
                    TicketType.price >= min_price,
                    TicketType.price <= max_price
                )
            elif min_price is not None:
                ticket_subquery = ticket_subquery.filter(TicketType.price >= min_price)
            elif max_price is not None:
                ticket_subquery = ticket_subquery.filter(TicketType.price <= max_price)
            
            events_query = events_query.filter(Event.id.in_(ticket_subquery))
        
        # Count total results
        total_count = events_query.count()
        
        # Apply pagination
        skip = (page - 1) * page_size
        events = events_query.order_by(Event.startDate.asc()).offset(skip).limit(page_size).all()
        
        return events, total_count
    
    def create(self, event_data: EventCreate, organizer_id: uuid.UUID) -> Event:
        """Create a new event"""
        db_event = Event(
            **event_data.dict(),
            organizer_id=organizer_id,
            status=EventStatus.DRAFT
        )
        
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        
        return db_event
    
    def update(self, event_id: str, event_data: EventUpdate) -> Optional[Event]:
        """Update an event"""
        event = self.get_by_id(event_id)
        if not event:
            return None
        
        update_data = event_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(event, field, value)
        
        event.updatedAt = func.now()
        
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def delete(self, event_id: str) -> bool:
        """Delete an event"""
        event = self.get_by_id(event_id)
        if not event:
            return False
        
        self.db.delete(event)
        self.db.commit()
        
        return True
    
    def publish(self, event_id: str) -> Optional[Event]:
        """Publish an event (change status from DRAFT to PUBLISHED)"""
        event = self.get_by_id(event_id)
        if not event:
            return None
        
        event.publish_event()
        
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def cancel(self, event_id: str) -> Optional[Event]:
        """Cancel an event"""
        event = self.get_by_id(event_id)
        if not event:
            return None
        
        event.cancel_event()
        
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def get_featured(self, limit: int = 6) -> List[Event]:
        """Get featured events (upcoming published events)"""
        return self.db.query(Event).filter(
            Event.status == EventStatus.PUBLISHED,
            Event.startDate >= datetime.now()
        ).order_by(Event.startDate.asc()).limit(limit).all()
    
    def count_by_organizer(self, organizer_id: uuid.UUID) -> int:
        """Count events by organizer"""
        return self.db.query(Event).filter(Event.organizer_id == organizer_id).count()
    
    def count_by_status(self, status: EventStatus) -> int:
        """Count events by status"""
        return self.db.query(Event).filter(Event.status == status).count()
    
    def get_tickets_sold(self, event_id: str) -> int:
        """Get total tickets sold for an event"""
        event = self.get_by_id(event_id)
        if not event or not event.ticket_types:
            return 0
        
        return sum(tt.sold_quantity for tt in event.ticket_types)
    
    def enrich_event_data(self, event: Event) -> Dict[str, Any]:
        """
        Enrich event with additional data (category, prices)
        Returns a dictionary ready for response
        """
        event_dict = event.to_dict()
        
        # Add category information
        if event.category:
            event_dict['category'] = {
                'id': str(event.category.id),
                'name': event.category.name,
                'slug': event.category.slug,
                'icon': event.category.icon,
                'color': event.category.color
            }
        
        # Add price information
        if event.ticket_types:
            prices = [tt.price for tt in event.ticket_types]
            event_dict['minPrice'] = min(prices) if prices else None
            event_dict['maxPrice'] = max(prices) if prices else None
        else:
            event_dict['minPrice'] = None
            event_dict['maxPrice'] = None
        
        return event_dict
