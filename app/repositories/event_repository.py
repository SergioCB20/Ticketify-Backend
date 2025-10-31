from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from app.models.event import Event, EventStatus
from app.models.user import User
from app.models.event_category import EventCategory

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_event(
        self,
        organizer_id: UUID,
        title: str,
        description: Optional[str],
        startDate: datetime,
        endDate: datetime,
        venue: str,
        totalCapacity: int,
        multimedia: Optional[List[str]] = None,
        category_id: Optional[UUID] = None
    ) -> Event:
        """Crear un nuevo evento"""
        event = Event(
            organizer_id=organizer_id,
            title=title,
            description=description,
            startDate=startDate,
            endDate=endDate,
            venue=venue,
            totalCapacity=totalCapacity,
            multimedia=multimedia or [],
            category_id=category_id,
            status=EventStatus.DRAFT
        )
        
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_event_by_id(self, event_id: UUID) -> Optional[Event]:
        """Obtener un evento por su ID con información relacionada"""
        return (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category)
            )
            .filter(Event.id == event_id)
            .first()
        )

    def get_events(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        status: Optional[EventStatus] = None,
        category_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[Event], int]:
        """Obtener eventos con filtros y paginación"""
        query = self.db.query(Event).options(
            joinedload(Event.organizer),
            joinedload(Event.category)
        )
        
        # Aplicar filtros
        filters = []
        
        if search:
            search_filter = or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%"),
                Event.venue.ilike(f"%{search}%")
            )
            filters.append(search_filter)
        
        if status:
            filters.append(Event.status == status)
        
        if category_id:
            filters.append(Event.category_id == category_id)
        
        if start_date:
            filters.append(Event.startDate >= start_date)
        
        if end_date:
            filters.append(Event.endDate <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Contar total
        total = query.count()
        
        # Aplicar paginación y ordenamiento
        events = (
            query
            .order_by(Event.startDate.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        
        return events, total

    def get_events_by_organizer(
        self,
        organizer_id: UUID,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Event], int]:
        """Obtener todos los eventos de un organizador"""
        query = (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category)
            )
            .filter(Event.organizer_id == organizer_id)
        )
        
        total = query.count()
        
        events = (
            query
            .order_by(Event.createdAt.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        
        return events, total

    def update_event(
        self,
        event_id: UUID,
        **kwargs
    ) -> Event:
        """Actualizar un evento"""
        event = self.get_event_by_id(event_id)
        
        if not event:
            raise ValueError("Event not found")
        
        # Actualizar solo los campos proporcionados
        for key, value in kwargs.items():
            if value is not None and hasattr(event, key):
                setattr(event, key, value)
        
        event.updatedAt = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event_status(
        self,
        event_id: UUID,
        new_status: EventStatus
    ) -> Event:
        """Actualizar el estado de un evento"""
        event = self.get_event_by_id(event_id)
        
        if not event:
            raise ValueError("Event not found")
        
        event.status = new_status
        event.updatedAt = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: UUID) -> bool:
        """Eliminar un evento"""
        event = self.get_event_by_id(event_id)
        
        if not event:
            raise ValueError("Event not found")
        
        self.db.delete(event)
        self.db.commit()
        return True

    def get_published_events(
        self,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Event], int]:
        """Obtener solo eventos publicados"""
        return self.get_events(
            page=page,
            page_size=page_size,
            status=EventStatus.PUBLISHED
        )

    def search_events(
        self,
        search_term: str,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Event], int]:
        """Buscar eventos por término"""
        return self.get_events(
            page=page,
            page_size=page_size,
            search=search_term
        )
