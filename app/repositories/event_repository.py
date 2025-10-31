from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.event import Event, EventStatus
from app.schemas.event import EventCreate, EventUpdate


class EventRepository:
    """Repository for Event database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_event(self, event_data: EventCreate, organizer_id: UUID) -> Event:
        """Create a new event"""
        event = Event(
            title=event_data.title,
            description=event_data.description,
            startDate=event_data.startDate,
            endDate=event_data.endDate,
            venue=event_data.venue,
            totalCapacity=event_data.totalCapacity,
            multimedia=event_data.multimedia if event_data.multimedia else [],
            category_id=event_data.category_id,
            organizer_id=organizer_id,
            status=EventStatus.DRAFT
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_event_by_id(self, event_id: UUID) -> Optional[Event]:
        """Get event by ID"""
        return self.db.query(Event).filter(Event.id == event_id).first()
    
    def get_events(
        self, 
        skip: int = 0, 
        limit: int = 10,
        status: Optional[EventStatus] = None,
        category_id: Optional[UUID] = None,
        organizer_id: Optional[UUID] = None,
        search: Optional[str] = None,
        start_date_from: Optional[datetime] = None,
        start_date_to: Optional[datetime] = None
    ) -> tuple[List[Event], int]:
        """Get list of events with filters"""
        query = self.db.query(Event)
        
        # Apply filters
        if status:
            query = query.filter(Event.status == status)
        
        if category_id:
            query = query.filter(Event.category_id == category_id)
        
        if organizer_id:
            query = query.filter(Event.organizer_id == organizer_id)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Event.title.ilike(search_term),
                    Event.description.ilike(search_term),
                    Event.venue.ilike(search_term)
                )
            )
        
        if start_date_from:
            query = query.filter(Event.startDate >= start_date_from)
        
        if start_date_to:
            query = query.filter(Event.startDate <= start_date_to)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering
        events = query.order_by(Event.startDate.asc()).offset(skip).limit(limit).all()
        
        return events, total
    
    def update_event(self, event_id: UUID, event_data: EventUpdate) -> Optional[Event]:
        """Update event"""
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        
        # Update only provided fields
        update_data = event_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        event.updatedAt = func.now()
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def delete_event(self, event_id: UUID) -> bool:
        """Delete event"""
        event = self.get_event_by_id(event_id)
        if not event:
            return False
        
        self.db.delete(event)
        self.db.commit()
        return True
    
    def update_event_status(self, event_id: UUID, status: EventStatus) -> Optional[Event]:
        """Update event status"""
        event = self.get_event_by_id(event_id)
        if not event:
            return None
        
        event.status = status
        event.updatedAt = func.now()
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_events_by_organizer(
        self, 
        organizer_id: UUID, 
        skip: int = 0, 
        limit: int = 10
    ) -> tuple[List[Event], int]:
        """Get events by organizer"""
        query = self.db.query(Event).filter(Event.organizer_id == organizer_id)
        total = query.count()
        events = query.order_by(Event.createdAt.desc()).offset(skip).limit(limit).all()
        return events, total
    
    def get_upcoming_events(self, skip: int = 0, limit: int = 10) -> tuple[List[Event], int]:
        """Get upcoming published events"""
        query = self.db.query(Event).filter(
            and_(
                Event.status == EventStatus.PUBLISHED,
                Event.startDate >= datetime.utcnow()
            )
        )
        total = query.count()
        events = query.order_by(Event.startDate.asc()).offset(skip).limit(limit).all()
        return events, total
    
    def get_featured_events(self, limit: int = 6) -> List[Event]:
        """Get featured events (published, upcoming, with available tickets)"""
        return self.db.query(Event).filter(
            and_(
                Event.status == EventStatus.PUBLISHED,
                Event.startDate >= datetime.utcnow()
            )
        ).order_by(Event.createdAt.desc()).limit(limit).all()
    
    def search_events(self, search_term: str, skip: int = 0, limit: int = 10) -> tuple[List[Event], int]:
        """Search events by title, description or venue"""
        search_pattern = f"%{search_term}%"
        query = self.db.query(Event).filter(
            and_(
                Event.status == EventStatus.PUBLISHED,
                or_(
                    Event.title.ilike(search_pattern),
                    Event.description.ilike(search_pattern),
                    Event.venue.ilike(search_pattern)
                )
            )
        )
        total = query.count()
        events = query.order_by(Event.startDate.asc()).offset(skip).limit(limit).all()
        return events, total
