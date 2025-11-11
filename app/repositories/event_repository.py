# app/repositories/event_repository.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, select
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from app.models.event import Event, EventStatus
from app.models.event_category import EventCategory
from app.models.ticket_type import TicketType
from app.schemas.event import EventCreate, EventUpdate


class EventRepository:
    """Repository unificado para operaciones de la base de datos de Eventos"""

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
    # 🔹 Obtener Evento por ID (con tickets y relaciones)
    # =========================================================
    def get_by_id(self, event_id: UUID) -> Optional[Event]:
        """
        Devuelve un evento por ID incluyendo:
        - organizer
        - category
        - ticket_types
        """
        event = (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)  # ✅ Cargar tipos de ticket
            )
            .filter(Event.id == event_id)
            .first()
        )

        # 🔍 Depuración
        if event:
            print("🟢 EVENTO ENCONTRADO:", event.title)
            print("🎟️ Ticket types encontrados:", len(event.ticket_types))
            for tt in event.ticket_types:
                print(f"➡️ {tt.name} | precio: {tt.price} | activo: {tt.is_active}")
        else:
            print("🔴 Evento no encontrado:", event_id)

        return event


    # =========================================================
    # 🔹 Actualizar Evento
    # =========================================================
    def update_event(self, event_id: UUID, event_data: EventUpdate) -> Optional[Event]:
        event = self.get_by_id(event_id)
        if not event:
            return None

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
    # 🔹 Listar todos los eventos
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

    # =========================================================
    # 🔹 Búsqueda avanzada de eventos (con filtros)
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

        query_filters = []

        # Estado
        if status:
            query_filters.append(Event.status == status)
        else:
            query_filters.append(Event.status == EventStatus.PUBLISHED)

        # Texto
        if query:
            query_filters.append(
                or_(
                    Event.title.ilike(f"%{query}%"),
                    Event.description.ilike(f"%{query}%")
                )
            )

        # Categoría
        if category_ids:
            query_filters.append(Event.category_id.in_(category_ids))

        # Lugar
        if location:
            query_filters.append(Event.venue.ilike(f"%{location}%"))
        if venue:
            query_filters.append(Event.venue.ilike(f"%{venue}%"))

        # Fecha
        if start_date:
            query_filters.append(Event.startDate >= start_date)
        if end_date:
            end_dt = end_date.replace(hour=23, minute=59, second=59)
            query_filters.append(Event.endDate <= end_dt)

        # Base Query
        events_query = self.db.query(Event).options(
            joinedload(Event.organizer),
            joinedload(Event.category),
            joinedload(Event.ticket_types)
        )

        if query_filters:
            events_query = events_query.filter(and_(*query_filters))

        # Filtro de precio (usa subquery)
        if min_price is not None or max_price is not None:
            ticket_sub = self.db.query(TicketType.event_id).distinct()
            if min_price is not None:
                ticket_sub = ticket_sub.filter(TicketType.price >= min_price)
            if max_price is not None:
                ticket_sub = ticket_sub.filter(TicketType.price <= max_price)
            events_query = events_query.filter(Event.id.in_(ticket_sub))

        total_count = events_query.count()

        events = (
            events_query
            .order_by(Event.startDate.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return events, total_count

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
    # 🔹 Otros utilitarios
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

    def get_featured_events(self, limit: int = 6) -> List[Event]:
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

    def count_by_organizer(self, organizer_id: UUID) -> int:
        return self.db.query(Event).filter(Event.organizer_id == organizer_id).count()

    def count_by_status(self, status: EventStatus) -> int:
        return self.db.query(Event).filter(Event.status == status).count()

    def get_tickets_sold(self, event_id: UUID) -> int:
        event = self.get_by_id(event_id)
        if not event or not getattr(event, "ticket_types", None):
            return 0
        return sum(tt["sold_quantity"] for tt in event.ticket_types if "sold_quantity" in tt)
