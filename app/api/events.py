from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importa las dependencias para obtener la BD y el usuario actual
from app.core.dependencies import get_db, get_current_organizer_user
from app.models.user import User
from app.schemas.event import OrganizerEventResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])

@router.get(
    "/organizer/me", 
    response_model=List[OrganizerEventResponse],
    summary="Obtener los eventos del organizador logueado"
)
def get_my_organizer_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_organizer_user)
):
    """
    Obtiene una lista de todos los eventos creados por el
    organizador autenticado actualmente.
    """
    event_service = EventService(db=db)
    events = event_service.get_organizer_events(organizer_id=current_user.id)
    return events
