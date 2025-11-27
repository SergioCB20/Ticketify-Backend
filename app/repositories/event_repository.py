# app/repositories/event_repository.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from app.models.event import Event, EventStatus
from app.models.event_category import EventCategory
from app.models.ticket_type import TicketType
from app.schemas.event import EventCreate, EventUpdate


class EventRepository:
    """Repositorio unificado para operaciones de eventos (fusion HEAD + main)"""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================
    # 🔹 Crear Evento
    # =========================================================
    def create_event(self, event_data: EventCreate, organizer_id: UUID) -> Event:
        db_event = Event(
            **event_data.dict(),
            organizer_id=organizer_id,
            status=EventStatus.DRAFT
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    # =========================================================
    # 🔹 Obtener Evento por ID (con relaciones)
    # =========================================================
    def get_by_id(self, event_id: UUID) -> Optional[Event]:
        event = (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)
            )
            .filter(Event.id == event_id)
            .first()
        )
        return event

    def get_event_by_id(self, event_id: UUID) -> Optional[Event]:
        """Alias de compatibilidad"""
        return self.get_by_id(event_id)

    # =========================================================
    # 🔹 Actualizar Evento
    # =========================================================
    def update_event(self, event_id: UUID, event_data: EventUpdate) -> Optional[Event]:
        event = self.get_by_id(event_id)
        if not event:
            return None

        # Solo actualiza lo que venga en el body
        update_data = event_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(event, field):
                setattr(event, field, value)
        

        event.updatedAt = func.now()
        self.db.commit()
        self.db.refresh(event)
        return event

    # =========================================================
    # 🔹 Eliminar Evento
    # =========================================================
    def delete_event(self, event_id: UUID) -> bool:
        event = self.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")

        self.db.delete(event)
        self.db.commit()
        return True

    # =========================================================
    # 🔹 Listar eventos (paginado)
    # =========================================================
    def get_all(self, skip: int = 0, limit: int = 20, status: Optional[EventStatus] = None) -> List[Event]:
        query = (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)
            )
        )

        if status:
            query = query.filter(Event.status == status)
        else:
            query = query.filter(Event.status == EventStatus.PUBLISHED)

        return (
            query.order_by(Event.startDate.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_events_by_organizer_id(self, organizer_id: UUID):
        return (
            self.db.query(Event)
            .filter(Event.organizer_id == organizer_id)
            .all()
        )


    # =========================================================
    # 🔹 Búsqueda avanzada (filtros, precio, fechas, etc.)
    # =========================================================
    def get_events(
        self,
        page: int = 1,
        page_size: int = 20,
        query: Optional[str] = None,
        category_ids: Optional[List[UUID]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        location: Optional[str] = None,
        venue: Optional[str] = None,
        status: Optional[EventStatus] = None
    ) -> Tuple[List[Event], int]:
        filters = [Event.status == (status or EventStatus.PUBLISHED)]

        if query:
            filters.append(or_(
                Event.title.ilike(f"%{query}%"),
                Event.description.ilike(f"%{query}%")
            ))
        if category_ids:
            filters.append(Event.category_id.in_(category_ids))
        if location:
            filters.append(Event.venue.ilike(f"%{location}%"))
        if venue:
            filters.append(Event.venue.ilike(f"%{venue}%"))
        if start_date:
            filters.append(Event.startDate >= start_date)
        if end_date:
            filters.append(Event.endDate <= end_date.replace(hour=23, minute=59, second=59))

        events_query = (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)
            )
            .filter(and_(*filters))
        )

        # Filtrar por rango de precios
        if min_price is not None or max_price is not None:
            ticket_sub = self.db.query(TicketType.event_id).distinct()
            if min_price is not None:
                ticket_sub = ticket_sub.filter(TicketType.price >= min_price)
            if max_price is not None:
                ticket_sub = ticket_sub.filter(TicketType.price <= max_price)
            events_query = events_query.filter(Event.id.in_(ticket_sub))

        total = events_query.count()
        events = (
            events_query
            .order_by(Event.startDate.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return events, total

    # =========================================================
    # 🔹 Búsqueda simple (para autocomplete o API ligera)
    # =========================================================
    def search_events(self, search_term: str, skip: int = 0, limit: int = 10) -> Tuple[List[Event], int]:
        pattern = f"%{search_term}%"
        query = self.db.query(Event).filter(
            and_(
                Event.status == EventStatus.PUBLISHED,
                or_(
                    Event.title.ilike(pattern),
                    Event.description.ilike(pattern),
                    Event.venue.ilike(pattern)
                )
            )
        )
        total = query.count()
        events = query.order_by(Event.startDate.asc()).offset(skip).limit(limit).all()
        return events, total

    # =========================================================
    # 🔹 Eventos por organizador
    # =========================================================
    def get_events_by_organizer_id(self, organizer_id: UUID) -> List[Event]:
        return (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)
            )
            .filter(Event.organizer_id == organizer_id)
            .order_by(Event.createdAt.desc())
            .all()
        )

    # =========================================================
    # 🔹 Estado del evento
    # =========================================================
    def publish_event(self, event_id: UUID) -> Optional[Event]:
        event = self.get_by_id(event_id)
        if not event:
            return None
        event.status = EventStatus.PUBLISHED
        self.db.commit()
        self.db.refresh(event)
        return event

    def cancel_event(self, event_id: UUID) -> Optional[Event]:
        event = self.get_by_id(event_id)
        if not event:
            return None
        event.status = EventStatus.CANCELLED
        self.db.commit()
        self.db.refresh(event)
        return event

    def set_draft_event(self, event_id: UUID) -> Optional[Event]:
        event = self.get_by_id(event_id)
        if not event:
            return None
        event.status = EventStatus.DRAFT
        event.updatedAt = func.now()
        self.db.commit()
        self.db.refresh(event)
        return event

    def complete_event(self, event_id: UUID) -> Optional[Event]:
        event = self.get_by_id(event_id)
        if not event:
            return None
        event.status = EventStatus.COMPLETED
        event.updatedAt = func.now()
        self.db.commit()
        self.db.refresh(event)
        return event

    # =========================================================
    # 🔹 Listar destacados / próximos
    # =========================================================
    def get_featured_events(self, limit: int = 6) -> List[Event]:
        """Publicados y con fecha futura."""
        return (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)
            )
            .filter(
                Event.status == EventStatus.PUBLISHED,
                Event.startDate >= datetime.utcnow()
            )
            .order_by(Event.startDate.asc())
            .limit(limit)
            .all()
        )

    def get_upcoming_events(self, skip: int = 0, limit: int = 10) -> Tuple[List[Event], int]:
        query = self.db.query(Event).filter(
            and_(
                Event.status == EventStatus.PUBLISHED,
                Event.startDate >= datetime.utcnow()
            )
        )
        total = query.count()
        events = query.order_by(Event.startDate.asc()).offset(skip).limit(limit).all()
        return events, total

    # =========================================================
    # 🔹 Métricas y conteos
    # =========================================================
    def count_by_organizer(self, organizer_id: UUID) -> int:
        return self.db.query(Event).filter(Event.organizer_id == organizer_id).count()

    def count_by_status(self, status: EventStatus) -> int:
        return self.db.query(Event).filter(Event.status == status).count()

    def get_tickets_sold(self, event_id: UUID) -> int:
        event = self.get_by_id(event_id)
        if not event or not getattr(event, "ticket_types", None):
            return 0
        return sum(
            tt.sold_quantity or 0
            for tt in event.ticket_types
        )
    
    # =========================================================
    # 🔹 Cambiar estado del evento
    # =========================================================
    def update_event_status(self, event_id: UUID, new_status: EventStatus):
        event = self.get_by_id(event_id)
        if not event:
            return None

        event.status = new_status
        event.updatedAt = func.now()

        self.db.commit()
        self.db.refresh(event)
        return event

    def update_event_photo(self, event_id: UUID, photo_bytes: bytes):
        event = self.get_by_id(event_id)
        if not event:
            return None
        event.photo = photo_bytes
        self.db.commit()
        self.db.refresh(event)
        return event

