from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate, PromotionResponse
from app.services import promotion_service
from app.utils.security import get_current_user  # <-- depende de cómo manejen autenticación JWT

router = APIRouter(
    prefix="/promotions",
    tags=["Promotions"]
)

# -----------------------------------------------------------
# 📌 Crear una promoción para un evento
# -----------------------------------------------------------
@router.post("/", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(
    promo_data: PromotionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear una promoción para un evento específico.
    Solo el organizador del evento puede hacerlo.
    """
    organizer_id = current_user["id"]  # 🔸 o current_user.id según tu auth.py
    return promotion_service.create_promotion_service(db, promo_data, organizer_id)


# -----------------------------------------------------------
# 📌 Obtener todas las promociones de un evento
# -----------------------------------------------------------
@router.get("/event/{event_id}", response_model=List[PromotionResponse])
def get_promotions_by_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar todas las promociones asociadas a un evento.
    """
    organizer_id = current_user["id"]
    return promotion_service.get_promotions_by_event_service(db, event_id, organizer_id)

# -----------------------------------------------------------
# 📌 Obtener todas las promociones (sin filtrar por evento)
# -----------------------------------------------------------
@router.get("/", response_model=List[PromotionResponse])
def get_all_promotions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar todas las promociones disponibles (según permisos).
    """
    organizer_id = current_user["id"]
    return promotion_service.get_all_promotions_service(db, organizer_id)

# -----------------------------------------------------------
# 📌 Actualizar promoción
# -----------------------------------------------------------
@router.put("/{promo_id}", response_model=PromotionResponse)
def update_promotion(
    promo_id: UUID,
    update_data: PromotionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar los detalles de una promoción existente.
    """
    organizer_id = current_user["id"]
    return promotion_service.update_promotion_service(db, promo_id, update_data, organizer_id)


# -----------------------------------------------------------
# 📌 Eliminar promoción
# -----------------------------------------------------------
@router.delete("/{promo_id}", status_code=status.HTTP_200_OK)
def delete_promotion(
    promo_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar una promoción (solo el organizador del evento).
    """
    organizer_id = current_user["id"]
    return promotion_service.delete_promotion_service(db, promo_id, organizer_id)
