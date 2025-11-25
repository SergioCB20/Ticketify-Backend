from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID
import os
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.event_service import EventService
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventDetailResponse,
    EventListResponse,
    OrganizerEventResponse,
    EventSearchResponse,
    MessageResponse,
    EventStatusUpdate
)
from app.models.event import EventStatus, Event
from app.models.user import User


# =========================================================
# 🔹 Router & Dependencia
# =========================================================
router = APIRouter(prefix="/events", tags=["Events"])

def get_event_service(db: Session = Depends(get_db)) -> EventService:
    """Inyección de dependencia para la capa de servicio"""
    return EventService(db)


# =========================================================
# 🔹 Búsqueda avanzada
# =========================================================
@router.get("/search", response_model=EventSearchResponse)
async def search_and_list_events(
    query: Optional[str] = Query(None, description="Búsqueda por título o descripción"),
    categories: Optional[str] = Query(None, description="Slugs de categorías separadas por comas"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    start_date: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)"),
    location: Optional[str] = Query(None, description="Ubicación geográfica (ciudad, región)"),
    venue: Optional[str] = Query(None, description="Nombre del local o recinto específico"),
    status: Optional[EventStatus] = Query(None, description="Estado del evento (DRAFT, PUBLISHED, etc.)"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Resultados por página"),
    event_service: EventService = Depends(get_event_service)
):
    """Búsqueda avanzada de eventos con filtros múltiples y paginación."""
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


# =========================================================
# 🔹 Listar eventos
# =========================================================

@router.get("/", response_model=List[EventResponse])
def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    event_service: EventService = Depends(get_event_service)
):
    """Obtener todos los eventos publicados (paginado simple)."""
    return event_service.get_all_events(skip=skip, limit=limit, status_filter=status)


@router.get("/active", response_model=List[EventResponse])
def get_active_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    event_service: EventService = Depends(get_event_service)
):
    """Obtener eventos activos (con fecha futura)."""
    events = event_service.event_repo.get_active_events(skip=skip, limit=limit, status_filter=status)
    return events


@router.get("/featured", response_model=List[EventResponse])
def get_featured_events(
    limit: int = Query(6, ge=1, le=20, description="Número de eventos destacados"),
    event_service: EventService = Depends(get_event_service)
):
    """Obtener eventos destacados (próximos eventos publicados)."""
    return event_service.get_featured_events(limit=limit)

# =========================================================
# 🔹 Obtener eventos del organizador autenticado
# =========================================================
@router.get("/my-events", response_model=List[OrganizerEventResponse])
async def get_my_events(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    event_service = EventService(db)
    events = event_service.get_events_by_organizer(current_user.id)

    # 🔥 Convertir Event → OrganizerEventResponse
    organizer_events = []
    for ev in events:
        organizer_events.append({
            "id": str(ev.id),
            "title": ev.title,
            "date": ev.startDate.isoformat(),
            "location": ev.venue,
            "totalTickets": ev.totalCapacity,
            "soldTickets": sum(tt['sold_quantity'] or 0 for tt in ev.ticket_types),
            "status": ev.status.value if hasattr(ev.status, "value") else ev.status,
            "imageUrl": ev.photoUrl
        })

    return organizer_events

@router.get("/by-organizer/{organizer_id}", response_model=List[EventResponse])
async def get_events_by_organizer_id(
    organizer_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Lista eventos vigentes de un organizador.
    """
    event_service = EventService(db)
    events = event_service.get_events_vigentes_by_organizer(organizer_id)
    return [e.to_dict() for e in events]


# =========================================================
# 🔹 Crear un evento
# =========================================================
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo evento (estado inicial: DRAFT)
    """
    event_service = EventService(db)
    return event_service.create_event(event_data, current_user.id)


# =========================================================
# 🔹 Obtener detalle de evento
# =========================================================
@router.get("/{event_id}", response_model=EventDetailResponse)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """Obtener detalle completo del evento por ID (con ticket_types)."""
    event_service = EventService(db)
    return event_service.get_event_by_id(event_id)


# =========================================================
# 🔹 Actualizar evento
# =========================================================

@router.put("/{event_id}")
async def update_event(
    event_id: UUID,
    event_data: EventUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    event_service = EventService(db)

    is_admin = any(role.name == "ADMIN" for role in current_user.roles) if current_user.roles else False

    updated = event_service.update_event(
        event_id=event_id,
        event_data=event_data,
        user_id=current_user.id,
        is_admin=is_admin,
    )

    # EventService.update_event ya devuelve un EventResponse (BaseModel)
    return updated
# =========================================================
# 🔹 Cambiar estado de evento
# =========================================================
@router.patch("/{event_id}/status", response_model=EventResponse)
async def update_event_status(
    event_id: UUID,
    status_data: EventStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cambiar el estado del evento (DRAFT, PUBLISHED, CANCELLED, COMPLETED).
    """
    event_service = EventService(db)
    is_admin = any(role.name == "ADMIN" for role in current_user.roles) if current_user.roles else False
    return event_service.update_event_status(
        event_id=event_id,
        new_status=status_data.status,
        user_id=current_user.id,
        is_admin=is_admin
    )


# =========================================================
# 🔹 Eliminar evento
# =========================================================
@router.delete("/{event_id}", response_model=MessageResponse)
async def delete_event(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete event
    
    Only the event organizer or an admin can delete the event.
    Cannot delete events that have sold tickets.
    """
    event_service = EventService(db)
    
    # Check if user is admin
    is_admin = any(role.name == "ADMIN" for role in current_user.roles) if current_user.roles else False
    
    return event_service.delete_event(
        event_id=event_id,
        user_id=current_user.id,
        is_admin=is_admin
    )


@router.post("/{event_id}/delete", response_model=MessageResponse)
async def delete_event_post(
    event_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete event vía POST (alternativa al DELETE)
    """
    event_service = EventService(db)

    is_admin = any(role.name == "ADMIN" for role in current_user.roles) if current_user.roles else False

    return event_service.delete_event(
        event_id=event_id,
        user_id=current_user.id,
        is_admin=is_admin
    )


@router.get("/{event_id}/photo")
async def get_event_photo(
    event_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Devuelve la foto del evento como imagen binaria.
    Se usa la URL construida en Event.to_dict(): /events/{id}/photo
    """
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event or not event.photo:
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    # Asumimos JPEG; cambia a image/png si guardas PNG, etc.
    return Response(content=event.photo, media_type="image/jpeg")

@router.post("/{event_id}/upload-photo", response_model=EventResponse)
async def upload_event_photo(
    event_id: UUID,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    event_service = EventService(db)

    # Leer bytes del archivo
    photo_bytes = await photo.read()

    # Guardar la foto en la DB
    updated_event = event_service.update_event_photo(event_id, photo_bytes)

    return updated_event

@router.get("/{event_id}/panel", response_model=EventDetailResponse)
async def get_event_panel(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    event_service = EventService(db)
    event = event_service.get_event_by_id(event_id)

    # opcional: asegurar que solo el organizador vea su panel
    if str(event.organizerId) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No estás autorizado para ver este panel"
        )

    return event