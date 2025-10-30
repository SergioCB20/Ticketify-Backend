# app/api/events.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Importa las dependencias para obtener la BD y el usuario actual
from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User # Importa el modelo User
from app.schemas.event import OrganizerEventResponse
from app.services.event_service import EventService
from app.models.role import RoleName # Importa los nombres de roles

router = APIRouter(prefix="/events", tags=["Events"])

@router.get(
    "organizer/me", 
    response_model=List[OrganizerEventResponse],
    summary="Obtener los eventos del organizador logueado"
)
async def get_my_organizer_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene una lista de todos los eventos creados por el
    organizador autenticado actualmente.
    """
    
    # --- Verificación de Seguridad ---
    # Nos aseguramos de que el usuario que hace la petición sea un ORGANIZER
    is_organizer = any(role.name == RoleName.ORGANIZER for role in current_user.roles)
    if not is_organizer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de organizador para ver esta información"
        )
    
    # Crea la instancia del servicio y obtén los datos
    event_service = EventService(db=db)
    events = await event_service.get_organizer_events(organizer_id=current_user.id)
    
    return events