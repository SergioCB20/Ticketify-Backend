from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.repositories.event_repository import EventRepository
from app.models.event import Event, EventStatus
from app.models.event_category import EventCategory
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventDetailResponse,
    EventResponse,
    EventSearchResponse,
    EventListResponse,
    MessageResponse
)
from app.models.ticket_type import TicketType


class EventService:
    """Capa de servicio para la lógica de negocio de eventos"""

    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db)

    # =========================================================
    # 🔹 Crear Evento
    # =========================================================
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

    # =========================================================
    # 🔹 Obtener un Evento
    # =========================================================
    def get_event_by_id(self, event_id: UUID) -> EventDetailResponse:
        """Obtiene un evento por su ID con detalles y ticket_types"""
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        event_dict = event.to_dict() if hasattr(event, "to_dict") else {}
        return EventDetailResponse(**event_dict)

    # =========================================================
    # 🔹 Listar Eventos Publicados
    # =========================================================
    def get_all_events(
        self,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None
    ) -> List[EventResponse]:
        """Obtiene todos los eventos (paginado)"""
        event_status = EventStatus.PUBLISHED
        if status_filter:
            try:
                event_status = EventStatus[status_filter.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail="Estado inválido")

        events = self.event_repo.get_all(skip=skip, limit=limit, status=event_status)
        return [self._event_to_response(e) for e in events]

    # =========================================================
    # 🔹 Eventos Activos (fechas futuras)
    # =========================================================
    def get_active_events(
        self,
        skip: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None
    ) -> List[EventResponse]:
        """Obtiene eventos futuros o activos"""
        event_status = EventStatus.PUBLISHED
        if status_filter:
            try:
                event_status = EventStatus[status_filter.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail="Estado inválido")

        events = self.event_repo.get_all(skip=skip, limit=limit, status=event_status)
        now = datetime.now(timezone.utc)
        upcoming = [e for e in events if getattr(e, "endDate", None) and e.endDate > now]
                
        return [self._event_to_response(e) for e in upcoming]
    

    def get_events_by_organizer(self, organizer_id: UUID):
        """
        Devuelve los eventos pertenecientes al organizador autenticado.
        Usa la función correcta del repositorio.
        """
        return self.event_repo.get_events_by_organizer_id(organizer_id)

    def get_events_vigentes_by_organizer(self, organizer_id: UUID):
        events = self.event_repo.get_events_by_organizer_id(organizer_id)

        # Fecha y hora actual aware (UTC)
        now = datetime.now(timezone.utc)

        vigentes = [
            e for e in events
            if e.status != EventStatus.CANCELLED and e.endDate >= now
        ]

        return vigentes

    # =========================================================
    # 🔹 Búsqueda Avanzada
    # =========================================================
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
        """Búsqueda de eventos con múltiples filtros"""

        # Validar estado
        event_status = EventStatus.PUBLISHED
        if status_filter:
            try:
                event_status = EventStatus[status_filter.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail="Estado inválido")

        # Procesar categorías (slugs → IDs)
        category_ids = None
        if categories:
            slugs = [c.strip() for c in categories.split(",") if c.strip()]
            if slugs:
                cats = (
                    self.db.query(EventCategory)
                    .filter(EventCategory.slug.in_(slugs), EventCategory.is_active == True)
                    .all()
                )
                if cats:
                    category_ids = [c.id for c in cats]
                else:
                    return EventSearchResponse(
                        events=[], total=0, page=page, page_size=page_size, total_pages=0
                    )

        # Procesar fechas
        start_dt = None
        end_dt = None
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de inicio inválido")
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha de fin inválido")

        # Consultar
        events, total = self.event_repo.get_events(
            query=query,
            category_ids=category_ids,
            min_price=min_price,
            max_price=max_price,
            start_date=start_dt,
            end_date=end_dt,
            location=location,
            venue=venue,
            status=event_status,
            page=page,
            page_size=page_size
        )

        total_pages = (total + page_size - 1) // page_size
        event_dicts = [e.to_dict() if hasattr(e, "to_dict") else {} for e in events]

        return EventSearchResponse(
            events=event_dicts,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    # =========================================================
    # 🔹 Actualizar Evento
    # =========================================================
    def update_event(
        self,
        event_id: UUID,
        event_data: EventUpdate,
        user_id: UUID,
        is_admin: bool = False
    ) -> EventResponse:
        """Actualiza un evento (organizador o admin)"""
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado")

        if event_data.startDate and event_data.endDate:
            if event_data.endDate <= event_data.startDate:
                raise HTTPException(status_code=400, detail="Fechas inválidas")

        updated = self.event_repo.update_event(event_id, event_data)
        
        return self._event_to_response(updated)

    # =========================================================
    # 🔹 Eliminar Evento
    # =========================================================
    def delete_event(self, event_id: UUID, user_id: UUID, is_admin: bool = False) -> MessageResponse:
        """Elimina un evento (solo organizador o admin)"""
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado")

        if event.available_tickets < event.totalCapacity:
            raise HTTPException(status_code=400, detail="No se puede eliminar un evento con ventas")

        self.event_repo.delete_event(event_id)
        return MessageResponse(message="Evento eliminado exitosamente")

    # =========================================================
    # 🔹 Cambiar Estado
    # =========================================================
    def update_event_status(
        self,
        event_id: UUID,
        new_status: str,
        user_id: UUID,
        is_admin: bool = False
    ) -> EventResponse:
        """Actualiza el estado de un evento"""
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado")

        try:
            status_enum = EventStatus[new_status.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail="Estado inválido")

        updated = self.event_repo.update_event_status(event_id, status_enum)
        return self._event_to_response(updated)

    # =========================================================
    # 🔹 Listar próximos / destacados
    # =========================================================
    def get_featured_events(self, limit: int = 6) -> List[EventResponse]:
        events = self.event_repo.get_featured_events(limit=limit)
        return [self._event_to_response(e) for e in events]

    def get_upcoming_events(self, page: int = 1, page_size: int = 10) -> EventListResponse:
        events, total = self.event_repo.get_upcoming_events(
            skip=(page - 1) * page_size, limit=page_size
        )
        event_responses = [self._event_to_response(e) for e in events]
        total_pages = (total + page_size - 1) // page_size
        return EventListResponse(
            events=event_responses,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    def update_event_photo(self, event_id: UUID, photo_bytes: bytes):
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        event.photo = photo_bytes
        event.updatedAt = datetime.now(datetime.timezone.utc)
        self.db.commit()
        self.db.refresh(event)
        return event


    # =========================================================
    # 🔹 Conversión
    # =========================================================
    def _event_to_response(self, event: Event) -> EventResponse:
        """Convierte modelo SQLAlchemy a esquema Pydantic"""
        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            startDate=event.startDate,
            endDate=event.endDate,
            venue=event.venue,
            totalCapacity=event.totalCapacity,
            status=event.status.value,
            availableTickets=getattr(event, "available_tickets", 0),
            isSoldOut=getattr(event, "is_sold_out", False),
            organizerId=event.organizer_id,
            categoryId=event.category_id,
            category=category_dict,
            minPrice=event.min_price,
            maxPrice=event.max_price,
            createdAt=event.createdAt,
            updatedAt=event.updatedAt,
            minPrice=event.min_price,
            maxPrice=event.max_price,
            ticket_types=[tt.to_dict() for tt in event.ticket_types]
        )
