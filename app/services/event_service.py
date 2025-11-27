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
        if event_data.startDate.astimezone(timezone.utc) <= datetime.now(timezone.utc):
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
        upcoming = [e for e in events if getattr(e, "endDate", None) and e.endDate.astimezone(timezone.utc) > now]
                
        return [self._event_to_response(e) for e in upcoming]
    

    def get_events_by_organizer(self, organizer_id: UUID):
        """
        Devuelve los eventos pertenecientes al organizador autenticado.
        Usa la función correcta del repositorio.
        """
        events = self.event_repo.get_events_by_organizer_id(organizer_id)
        return [self._event_to_response(e) for e in events]

    def get_events_vigentes_by_organizer(self, organizer_id: UUID):
        events = self.event_repo.get_events_by_organizer_id(organizer_id)

        # Fecha y hora actual aware (UTC)
        now = datetime.now(timezone.utc)

        vigentes = [
            e for e in events
            if e.status != EventStatus.CANCELLED and e.endDate.astimezone(timezone.utc) >= now
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
        is_admin: bool = False,
    ) -> EventResponse:
        event = (
            self.db.query(Event)
            .filter(Event.id == event_id)
            .first()
        )
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(status_code=403, detail="No autorizado")

        # datos a actualizar (solo los campos enviados)
        update_data = event_data.dict(exclude_unset=True)

        # validar fechas si vienen en el payload
        start_date = update_data.get("startDate") or update_data.get("start_date")
        end_date = update_data.get("endDate") or update_data.get("end_date")
        if start_date and end_date and end_date <= start_date:
            raise HTTPException(status_code=400, detail="Fechas inválidas")

        for field, value in update_data.items():
            if hasattr(event, field):
                setattr(event, field, value)

        event.updatedAt = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(event)

        return self._event_to_response(event)
    # =========================================================
    # 🔹 Eliminar Evento
    # =========================================================
    def delete_event(
            self,
            event_id: UUID,
            user_id: UUID,
            is_admin: bool = False,
        ) -> MessageResponse:
        # buscar evento
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        # solo organizador o admin
        if not is_admin and event.organizer_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="No estás autorizado para eliminar este evento",
            )
            
        self.db.delete(event)
        self.db.commit()

        return MessageResponse(message="Evento eliminado correctamente")

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

        # Verificar si está cambiando a PUBLISHED
        old_status = event.status
        updated = self.event_repo.update_event_status(event_id, status_enum)

        # Si el evento cambió a PUBLISHED, enviar notificaciones
        if old_status != EventStatus.PUBLISHED and status_enum == EventStatus.PUBLISHED:
            self._send_new_event_notifications(updated)

        return self._event_to_response(updated)

    def _send_new_event_notifications(self, event):
        """Enviar notificaciones por email a usuarios suscritos a la categoría del evento"""
        try:
            from app.services.preferences_service import PreferencesService
            from app.utils.email_service import email_service

            # Obtener usuarios suscritos a esta categoría
            # Usamos 24 horas como cooldown para evitar spam
            preferences_service = PreferencesService(self.db)
            subscribers = preferences_service.get_users_subscribed_to_category(
                category_id=event.category_id,
                hours_since_last_notification=24  # 24 horas de cooldown
            )

            if not subscribers:
                print(f"[NOTIFICATION] No hay usuarios suscritos a la categoría del evento {event.title}")
                return

            # Obtener información de la categoría
            category = event.category
            category_name = category.name if category else "Sin categoría"

            # Formatear fecha
            event_date = event.startDate.strftime("%d/%m/%Y %H:%M") if event.startDate else "Por confirmar"

            # URL del evento (ajustar según tu frontend)
            frontend_url = "http://localhost:3000"  # Cambiar en producción
            event_url = f"{frontend_url}/events/{event.id}"

            # Enviar emails a cada suscriptor
            notifications_sent = 0
            for user in subscribers:
                try:
                    success = email_service.send_new_event_notification(
                        to_email=user.email,
                        first_name=user.firstName,
                        event_title=event.title,
                        event_description=event.description or "Sin descripción",
                        category_name=category_name,
                        event_date=event_date,
                        event_location=event.venue or "Por confirmar",
                        event_url=event_url
                    )

                    if success:
                        # Marcar que se envió la notificación
                        preferences_service.mark_notification_sent(user.id, event.category_id)
                        notifications_sent += 1
                except Exception as e:
                    print(f"[ERROR] Error enviando notificación a {user.email}: {str(e)}")
                    continue

            print(f"[NOTIFICATION] Se enviaron {notifications_sent} notificaciones para el evento '{event.title}'")

        except Exception as e:
            # No fallar la actualización del evento si falla el envío de notificaciones
            print(f"[ERROR] Error en el sistema de notificaciones: {str(e)}")
            import traceback
            traceback.print_exc()

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
        event.updatedAt = datetime.now(timezone.utc)  
        self.db.commit()
        self.db.refresh(event)
        return event


    # =========================================================
    # 🔹 Conversión
    # =========================================================
    def _event_to_response(self, event: Event) -> EventResponse:
        """Convierte modelo SQLAlchemy a esquema Pydantic"""
        # Crear diccionario de categoría si existe
        category_dict = None
        if event.category:
            category_dict = {
                "id": str(event.category.id),
                "name": event.category.name,
                "slug": event.category.slug,
                "description": event.category.description,
                "icon": event.category.icon,
                "colorCode": event.category.color,
                "isActive": event.category.is_active,
                "isFeatured": event.category.is_featured,
                "sortOrder": event.category.sort_order
            }
        
        # Construir la lista de tipos de ticket de forma imperativa antes del return
        ticket_types_list = []
        if getattr(event, "ticket_types", None):
            for tt in event.ticket_types:
                if tt is not None:
                    ticket_types_list.append({
                        "id": str(tt.id),
                        "name": tt.name,
                        "price": float(tt.price) if tt.price else None,
                        "quantity_available": tt.quantity_available, # La clave que necesita el router
                        "sold_quantity": tt.sold_quantity, # La clave que necesita el router
                        
                        # (Puedes añadir los otros campos del ticket aquí si los necesitas)
                        "description": tt.description,
                        "original_price": float(tt.original_price) if tt.original_price else None,
                        "min_purchase": tt.min_purchase,
                        "max_purchase": tt.max_purchase,
                        "is_active": tt.is_active
                    })

        return EventResponse(
            id=event.id,
            title=event.title,
            description=event.description,
            startDate=event.startDate,
            endDate=event.endDate,
            venue=event.venue,
            totalCapacity=event.totalCapacity,
            status=event.status.value,
            photoUrl=f"/api/events/{event.id}/photo" if event.photo else None,
            availableTickets=getattr(event, "available_tickets", 0),
            isSoldOut=getattr(event, "is_sold_out", False),
            organizerId=event.organizer_id,
            categoryId=event.category_id,
            category=category_dict,
            minPrice=event.min_price,
            maxPrice=event.max_price,
            createdAt=event.createdAt,
            updatedAt=event.updatedAt,
            ticket_types=ticket_types_list
        )
