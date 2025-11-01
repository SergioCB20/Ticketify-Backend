# events_router.py (Versión Unificada)

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# Dependencias principales
from app.core.dependencies import get_db, get_current_user
from app.services.event_service import EventService  # Usando la capa de servicio
from app.models.user import User
from app.models.event import EventStatus

# Esquemas de Pydantic
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,    # Esquema de lista con paginación
    EventDetailResponse   # Esquema detallado para un solo evento
)

router = APIRouter(prefix="/events", tags=["events"])

# --- Dependencia del Servicio ---

def get_event_service(db: Session = Depends(get_db)) -> EventService:
    """Dependencia para inyectar la capa de servicio de eventos"""
    return EventService(db)

# --- Endpoints ---

@router.get("/", response_model=EventListResponse)
async def search_and_list_events(
    query: Optional[str] = Query(None, description="Búsqueda por título o descripción"),
    categories: Optional[str] = Query(None, description="Slugs de categorías separadas por comas"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    start_date: Optional[datetime] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    location: Optional[str] = Query(None, description="Ubicación geográfica (ciudad, región)"),
    venue: Optional[str] = Query(None, description="Nombre del local o recinto específico"),
    status: Optional[EventStatus] = Query(None, description="Estado del evento (DRAFT, PUBLISHED, etc.)"),
    
    organizer_id: Optional[UUID] = Query(None, description="Filtrar por ID de organizador"),
    
    # Paginación (de ambos)
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Resultados por página"),
    
    event_service: EventService = Depends(get_event_service)
):
    """
    Búsqueda avanzada de eventos con filtros múltiples y paginación.
    Combina la funcionalidad de listado general, búsqueda y filtrado por organizador.
    """
    # El servicio se encarga de la lógica de búsqueda y paginación
    return event_service.search_events(
        query=query,
        categories=categories,
        min_price=min_price,
        max_price=max_price,
        start_date=start_date,
        end_date=end_date,
        location=location,
        venue=venue,
        status_filter=status,
        organizer_id=organizer_id,
        page=page,
        page_size=page_size
    )


@router.get("/featured", response_model=List[EventResponse])
async def get_featured_events(
    limit: int = Query(6, ge=1, le=20, description="Número de eventos destacados"),
    event_service: EventService = Depends(get_event_service)
):
    """
    Obtener eventos destacados (próximos eventos publicados).
    """
    return event_service.get_featured_events(limit=limit)


@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Crear un nuevo evento. Requiere autenticación.
    """
    # El servicio maneja la creación y la asignación del organizer_id
    return event_service.create_event(event_data, current_user.id)


@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: UUID,  # Usando UUID para validación
    event_service: EventService = Depends(get_event_service)
):
    """
    Obtener detalles de un evento específico por su ID.
    """
    # El servicio maneja la lógica de "no encontrado" (404)
    return event_service.get_event_by_id(event_id)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: UUID,  # Usando UUID
    event_data: EventUpdate,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Actualizar un evento existente.
    Solo el organizador del evento puede actualizarlo.
    """
    # El servicio maneja la lógica de permisos (403) y "no encontrado" (404)
    return event_service.update_event(event_id, event_data, current_user.id)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: UUID,  # Usando UUID
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Eliminar un evento.
    Solo el organizador del evento puede eliminarlo.
    """
    # El servicio maneja la lógica de permisos (403) y "no encontrado" (404)
    event_service.delete_event(event_id, current_user.id)
    # No se retorna contenido en un 204
    return None


@router.post("/{event_id}/publish", response_model=EventResponse)
async def publish_event(
    event_id: UUID,  # Usando UUID
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Publicar un evento (cambiar de DRAFT a PUBLISHED).
    Solo el organizador puede hacerlo.
    """
    return event_service.publish_event(event_id, current_user.id)


@router.post("/{event_id}/cancel", response_model=EventResponse)
async def cancel_event(
    event_id: UUID,  # Usando UUID
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Cancelar un evento (cambiar estado a CANCELLED).
    Solo el organizador puede hacerlo.
    """
    return event_service.cancel_event(event_id, current_user.id)


@router.post("/{event_id}/draft", response_model=EventResponse)
async def set_event_draft(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Poner el evento en estado DRAFT.
    Solo el organizador puede hacerlo.
    """
    return event_service.set_draft_event(event_id, current_user.id)


@router.post("/{event_id}/complete", response_model=EventResponse)
async def complete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Marcar el evento como COMPLETED.
    Solo el organizador puede hacerlo.
    """
    return event_service.complete_event(event_id, current_user.id)

def get_organizer_events(self, organizer_id: uuid.UUID) -> list[OrganizerEventResponse]:
        # 1. Pide los eventos a la BD
        db_events = self.event_repo.get_events_by_organizer_id(organizer_id)
        
        response_events = []
        for event in db_events:
            # 2. Lógica de negocio (Calcular tickets vendidos)
            stmt = select(func.count(Ticket.id)).where(
                Ticket.event_id == event.id,
                Ticket.status.notin_(['CANCELLED'])
            )
            sold_tickets_count = self.db.execute(stmt).scalar_one()

            # 3. Lógica de negocio (Obtener imagen principal)
            main_image_url = event.multimedia[0] if event.multimedia else None

            # 4. "Traduce" los nombres de la BD a los nombres del Frontend
            response_event_data = {
                "id": event.id,
                "title": event.title,
                "date": event.startDate,  # BD (start_date) -> Frontend (date)
                "location": event.venue,   # BD (venue) -> Frontend (location)
                "totalTickets": event.totalCapacity,
                "soldTickets": sold_tickets_count,
                "status": str(event.status.value),
                "imageUrl": main_image_url
            }

            # 5. Valida y agrega a la lista final
            response_events.append(OrganizerEventResponse.model_validate(response_event_data))
        
        return response_events