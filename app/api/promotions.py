from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.database import get_db
from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate, PromotionResponse
from app.services import promotion_service
from app.utils.security import get_current_user  # depende de tu JWT/auth

router = APIRouter(
    prefix="/promotions",
    tags=["Promotions"]
)

# -----------------------------------------------------------
# 📌 Crear una promoción
# -----------------------------------------------------------
@router.post("/", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(
    promo_data: PromotionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crear una nueva promoción (por organizador o admin).
    """
    return promotion_service.create_promotion(
        db=db,
        name=promo_data.name,
        code=promo_data.code,
        promotion_type=promo_data.promotion_type,
        discount_value=promo_data.discount_value,
        start_date=promo_data.start_date,
        end_date=promo_data.end_date,
        created_by_id=promo_data.created_by_id,
        description=promo_data.description,
        max_discount_amount=promo_data.max_discount_amount,
        min_purchase_amount=promo_data.min_purchase_amount,
        max_uses=promo_data.max_uses,
        max_uses_per_user=promo_data.max_uses_per_user,
        applies_to_all_events=promo_data.applies_to_all_events,
        applies_to_new_users_only=promo_data.applies_to_new_users_only,
        is_public=promo_data.is_public,
        event_id=promo_data.event_id
    )


# -----------------------------------------------------------
# 📌 Obtener todas las promociones activas
# -----------------------------------------------------------
@router.get("/", response_model=List[PromotionResponse])
def get_all_promotions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar todas las promociones activas y vigentes.
    """
    return promotion_service.get_active_promotions(db)


# -----------------------------------------------------------
# 📌 Obtener promociones de un evento
# -----------------------------------------------------------
@router.get("/event/{event_id}", response_model=List[PromotionResponse])
def get_promotions_by_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Listar todas las promociones asociadas a un evento específico.
    """
    promotions = promotion_service.get_promotions_by_event(db, event_id)
    if not promotions:
        raise HTTPException(status_code=404, detail="No se encontraron promociones para este evento.")
    return promotions


# -----------------------------------------------------------
# 📌 Actualizar una promoción
# -----------------------------------------------------------
@router.put("/{promo_id}", response_model=PromotionResponse)
def update_promotion(
    promo_id: UUID,
    update_data: PromotionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar una promoción existente.
    """
    updated = promotion_service.update_promotion(db, promo_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Promoción no encontrada.")
    return updated


# -----------------------------------------------------------
# 📌 Eliminar una promoción
# -----------------------------------------------------------
@router.delete("/{promo_id}", status_code=status.HTTP_200_OK)
def delete_promotion(
    promo_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar una promoción existente.
    """
    success = promotion_service.delete_promotion(db, promo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Promoción no encontrada.")
    return {"message": "Promoción eliminada correctamente."}
