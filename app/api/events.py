from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.services.event_service import EventService
from app.schemas.event import EventResponse, EventCreate, EventUpdate, EventSearchResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/events", tags=["events"])


def get_event_service(db: Session = Depends(get_db)) -> EventService:
    """Dependency to get EventService instance"""
    return EventService(db)


@router.get("/search", response_model=EventSearchResponse)
def search_events(
    query: Optional[str] = Query(None, description="Búsqueda por título, descripción o artista"),
    categories: Optional[str] = Query(None, description="Slugs de categorías separadas por comas"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    location: Optional[str] = Query(None, description="Ubicación geográfica (ciudad, región)"),
    venue: Optional[str] = Query(None, description="Nombre del local o recinto específico"),
    status: Optional[str] = Query(None, description="Estado del evento"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Resultados por página"),
    event_service: EventService = Depends(get_event_service)
):
    """
    Buscar eventos con múltiples filtros avanzados.
    
    **Parámetros:**
    - **query**: Búsqueda de texto libre en título y descripción
    - **categories**: Lista de categorías separadas por comas (ej: "conciertos,deportes")
    - **min_price/max_price**: Rango de precios de tickets
    - **start_date/end_date**: Rango de fechas del evento
    - **location**: Filtrar por ubicación geográfica (ciudad, región)
    - **venue**: Filtrar por nombre específico del local o recinto
    - **status**: Estado del evento (DRAFT, PUBLISHED, CANCELLED, COMPLETED)
    - **page/page_size**: Paginación
    
    **Retorna:**
    - Lista de eventos que cumplen con los criterios
    - Metadata de paginación (total, página actual, etc.)
    """
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
        page=page,
        page_size=page_size
    )


@router.get("/", response_model=List[EventResponse])
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    event_service: EventService = Depends(get_event_service)
):
    """
    Obtener todos los eventos publicados con paginación simple
    """
    return event_service.get_all_events(skip=skip, limit=limit, status_filter=status)


@router.get("/featured/list", response_model=List[EventResponse])
def get_featured_events(
    limit: int = Query(6, ge=1, le=20, description="Número de eventos destacados"),
    event_service: EventService = Depends(get_event_service)
):
    """
    Obtener eventos destacados (próximos eventos con más ventas o mejor calificados)
    """
    return event_service.get_featured_events(limit=limit)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: str,
    event_service: EventService = Depends(get_event_service)
):
    """
    Obtener un evento específico por ID
    """
    return event_service.get_event_by_id(event_id)


@router.post("/", response_model=EventResponse)
def create_event(
    event: EventCreate,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Crear un nuevo evento (requiere autenticación)
    """
    return event_service.create_event(event, current_user.id)


@router.put("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    event_update: EventUpdate,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Actualizar un evento (solo el organizador)
    """
    return event_service.update_event(event_id, event_update, current_user.id)


@router.delete("/{event_id}")
def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Eliminar un evento (solo el organizador)
    """
    return event_service.delete_event(event_id, current_user.id)


@router.post("/{event_id}/publish", response_model=EventResponse)
def publish_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Publicar un evento (cambiar de DRAFT a PUBLISHED)
    """
    return event_service.publish_event(event_id, current_user.id)


@router.post("/{event_id}/cancel", response_model=EventResponse)
def cancel_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Cancelar un evento
    """
    return event_service.cancel_event(event_id, current_user.id)


@router.get("/organizer/{organizer_id}", response_model=List[EventResponse])
def get_organizer_events(
    organizer_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    event_service: EventService = Depends(get_event_service)
):
    """
    Obtener eventos de un organizador específico (requiere autenticación)
    """
    import uuid
    
    # Verify user is requesting their own events or is admin
    if str(current_user.id) != organizer_id:
        # TODO: Check if user is admin
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para ver eventos de otro organizador"
        )
    
    return event_service.get_organizer_events(
        uuid.UUID(organizer_id), 
        skip=skip, 
        limit=limit
    )
