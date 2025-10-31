from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

# Importa las dependencias para obtener la BD y el usuario actual
from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User # Importa el modelo User
from app.schemas.event import OrganizerEventResponse
from app.services.event_service import EventService
# --- Import de RoleName quitado ---

router = APIRouter(prefix="/events", tags=["Events"])

@router.get(
    "/organizer/me", 
    response_model=List[OrganizerEventResponse],
    summary="Obtener los eventos del organizador logueado"
)
async def get_my_organizer_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # <-- Aún necesitamos saber QUIÉN está logueado
):
    """
    Obtiene una lista de todos los eventos creados por el
    organizador autenticado actualmente.
    """
    
    # --- Verificación de Seguridad quitada ---
    # NOTA: Ahora, cualquier usuario logueado (asistente o admin)
    # puede llamar a este endpoint. Se asume que el frontend
    # es quien decide si mostrar o no el botón para llamarlo.
    
    # Crea la instancia del servicio y obtén los datos
    # Usa el ID del usuario logueado (current_user.id) para buscar sus eventos
    event_service = EventService(db=db)
    events = await event_service.get_organizer_events(organizer_id=current_user.id)
    
    return events