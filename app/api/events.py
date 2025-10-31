from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.event_schema import EventOut, EventCreate, EventUpdate, PromotionOut
from app.services.event_service import EventService
from app.utils.security import get_current_user
from app.core.database import get_db

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


# =========================================================
# 🟢 Obtener eventos del organizador autenticado
# =========================================================
@router.get("/{user_id}", response_model=List[EventOut])
def get_events_by_organizer(
    user_id: UUID,
    db: Session = Depends(get_db)#,
    #current_user=Depends(get_current_user)
):
    """
    Devuelve todos los eventos publicados del organizador autenticado.
    """
    try:
        events = EventService.get_events_by_organizer(db, str(user_id))
        return [e.to_dict() for e in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# 🔍 Obtener un evento por ID
# =========================================================
@router.get("/{event_id}", response_model=EventOut)
def get_event_by_id(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Devuelve un evento específico por su ID.
    """
    event = EventService.get_event_by_id(db, str(event_id))
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if str(event.organizer_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este evento")
    return event


# =========================================================
# 🧾 Obtener promociones asociadas a un evento
# =========================================================
@router.get("/{event_id}/promotions", response_model=List[PromotionOut])
def get_event_promotions(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Devuelve las promociones asociadas a un evento del organizador autenticado.
    """
    try:
        promotions = EventService.get_promotions_for_event(db, str(event_id), 
                                            current_user["id"] if isinstance(current_user, dict) else current_user.id)
        print("✅ PROMOTIONS ->", promotions)
        # Si ya son dicts, devuélvelos directamente
        if isinstance(promotions, list) and all(isinstance(p, dict) for p in promotions):
            return promotions

        # Si son objetos ORM, conviértelos
        return [p.to_dict() if hasattr(p, "to_dict") else p for p in promotions]
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("❌ ERROR get_event_promotions:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# 🟩 Crear un nuevo evento
# =========================================================
@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Crea un nuevo evento para el organizador autenticado.
    """
    try:
        event = EventService.create_event(db, payload, current_user.id)
        return event
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# ✏️ Actualizar un evento existente
# =========================================================
@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: UUID,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Actualiza los datos de un evento existente (solo si pertenece al organizador autenticado).
    """
    try:
        updated = EventService.update_event(db, str(event_id), payload, current_user.id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# 🗑️ Eliminar un evento
# =========================================================
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Elimina un evento del organizador autenticado.
    """
    try:
        EventService.delete_event(db, str(event_id), current_user.id)
        return {"detail": "Evento eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
