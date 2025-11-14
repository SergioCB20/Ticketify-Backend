# event_repository.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, select
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime

# Importa todos los modelos y esquemas necesarios
from app.models.event import Event, EventStatus
from app.models.user import User  # Asumiendo que existe para la relación 'organizer'
from app.models.event_category import EventCategory
from app.models.ticket_type import TicketType
from app.schemas.event import EventCreate, EventUpdate  # Asumiendo que estos esquemas existen


class EventRepository:
    """Repository unificado para operaciones de la base de datos de Eventos"""

    def __init__(self, db: Session):
        self.db = db

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

    def get_by_id(self, event_id: UUID) -> Optional[Event]:
       
        return (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)  # Cargar ticket_types para calcular precios
            )
            .filter(Event.id == event_id)
            .first()
        )
    
    def get_event_by_id(self, event_id: UUID) -> Optional[Event]:
        """Alias method for get_by_id to maintain compatibility"""
        return self.get_by_id(event_id)

    def update_event(self, event_id: UUID, event_data: EventUpdate) -> Optional[Event]:
       
        event = self.get_by_id(event_id)
        if not event:
            return None
        
        # Usar exclude_unset=True permite actualizaciones parciales (PATCH)
        update_data = event_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(event, field):
                setattr(event, field, value)
        
        # Usar func.now() utiliza la marca de tiempo de la BD
        event.updatedAt = func.now() 
        
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: UUID) -> bool:
        
        event = self.get_by_id(event_id)
        
        if not event:
            raise ValueError("Event not found")
        
        self.db.delete(event)
        self.db.commit()
        return True
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[EventStatus] = None
    ) -> List[Event]:
        """
        Retrieve events with pagination and optional status filter.

        Parameters:
            skip (int): number of records to skip (offset)
            limit (int): maximum number of records to return
            status (Optional[EventStatus]): filter by event status; if None, defaults to PUBLISHED

        Returns:
            List[Event]: A list of events matching the criteria
        """
        query = (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)  # Cargar ticket_types para calcular precios
            )
        )

        if status:
            query = query.filter(Event.status == status)
        else:
            query = query.filter(Event.status == EventStatus.PUBLISHED)

        events = (
            query
            .order_by(Event.startDate.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return events

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
        
        # Filtro de estado
        if status:
            query_filters.append(Event.status == status)
        else:
            # Por defecto, solo busca eventos publicados si no se especifica estado
            query_filters.append(Event.status == EventStatus.PUBLISHED)
        
        # Búsqueda por texto
        if query:
            text_filter = or_(
                Event.title.ilike(f"%{query}%"),
                Event.description.ilike(f"%{query}%")
            )
            query_filters.append(text_filter)
        
        # Filtro de categoría
        if category_ids:
            query_filters.append(Event.category_id.in_(category_ids))
        
        # Filtros de ubicación
        if location:
            query_filters.append(Event.venue.ilike(f"%{location}%"))
        
        if venue:
            query_filters.append(Event.venue.ilike(f"%{venue}%"))
        
        # Filtros de fecha
        if start_date:
            query_filters.append(Event.startDate >= start_date)
        
        if end_date:
            # Ajustar end_date para que incluya todo el día
            end_datetime = end_date.replace(hour=23, minute=59, second=59)
            query_filters.append(Event.endDate <= end_datetime)
        
        # Construir la consulta base con joinedload para cargar relaciones
        events_query = self.db.query(Event).options(
            joinedload(Event.organizer),
            joinedload(Event.category),
            joinedload(Event.ticket_types)  # Cargar ticket_types para calcular precios
        )

        if query_filters:
            events_query = events_query.filter(and_(*query_filters))
        
        # Filtro de precio (requiere subconsulta o join con TicketType)
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
        
        # Contar total de resultados *antes* de la paginación
        total_count = events_query.count()
        
        # Aplicar paginación y ordenamiento
        skip = (page - 1) * page_size
        events = (
            events_query
            .order_by(Event.startDate.asc())
            .offset(skip)
            .limit(page_size)
            .all()
        )
        
        return events, total_count

    def get_events_by_organizer_id(
        self,
        organizer_id: UUID,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Event], int]:
        
        query = (
            self.db.query(Event)
            .options(
                joinedload(Event.organizer),
                joinedload(Event.category),
                joinedload(Event.ticket_types)  # Cargar ticket_types para calcular precios
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

    def publish_event(self, event_id: UUID) -> Optional[Event]:
        
        event = self.get_by_id(event_id)
        if not event:
            return None
        
        # Asumiendo que el modelo Event tiene un método publish_event()
        # Si no, se haría: event.status = EventStatus.PUBLISHED
        event.publish_event()  
        
        self.db.commit()
        self.db.refresh(event)
        return event

    def cancel_event(self, event_id: UUID) -> Optional[Event]:
        
        event = self.get_by_id(event_id)
        if not event:
            return None
        
        # Asumiendo que el modelo Event tiene un método cancel_event()
        # Si no, se haría: event.status = EventStatus.CANCELLED
        event.cancel_event()
        
        self.db.commit()
        self.db.refresh(event)
        return event

    def set_draft_event(self, event_id: UUID) -> Optional[Event]:
        """
        Poner el evento en estado DRAFT.
        """
        event = self.get_by_id(event_id)
        if not event:
            return None

        # Cambiar estado a DRAFT
        event.status = EventStatus.DRAFT
        event.updatedAt = func.now()

        self.db.commit()
        self.db.refresh(event)
        return event

    def complete_event(self, event_id: UUID) -> Optional[Event]:
        """
        Marcar el evento como COMPLETED.
        """
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
                joinedload(Event.ticket_types)  # Cargar ticket_types para calcular precios
            )
            .filter(
                Event.status == EventStatus.PUBLISHED,
                Event.startDate >= datetime.utcnow() # Usar utcnow() si las fechas son UTC
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
        
        # Usamos get_by_id para obtener el evento
        event = self.get_by_id(event_id)
        if not event:
            return 0
            
        # Cargar explícitamente los ticket_types si no se cargaron con get_by_id
        # (Aunque get_by_id no los carga, la relación 'lazy' los cargará aquí)
        if not event.ticket_types:
            return 0
        
        return sum(tt.sold_quantity for tt in event.ticket_types)
    
    def get_events_by_organizer_id(self, organizer_id: UUID) -> list[Event]:
        stmt = select(Event).where(Event.organizer_id == organizer_id)
        result = self.db.execute(stmt)
        return result.scalars().all()
