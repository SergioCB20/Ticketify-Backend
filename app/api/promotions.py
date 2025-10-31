from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.promotion_schema import PromotionResponse, PromotionCreate, PromotionUpdate
from app.services.promotion_service import PromotionService
from app.utils.security import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/promotions", tags=["Promotions"])


# =========================================================
# 🔹 Obtener todas las promociones (modo admin o prueba)
# =========================================================
@router.get("/", response_model=List[PromotionResponse])
def get_all_promotions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        promotions = PromotionService.get_all(db)
        return promotions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# 🔹 Obtener una promoción por ID
# =========================================================
@router.get("/{promotion_id}", response_model=PromotionResponse)
def get_promotion_by_id(
    promotion_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        promo = PromotionService.get_by_id(db, str(promotion_id))
        if not promo:
            raise HTTPException(status_code=404, detail="Promoción no encontrada")
        return promo
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# 🔹 Crear una nueva promoción
# =========================================================
@router.post("/", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
def create_promotion(
    payload: PromotionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Crea una nueva promoción asociada a un evento.
    """
    try:
        print("📦 Payload recibido en FastAPI:", payload)
        print("📦 Payload dict():", payload.dict())  # 👈 añade esta línea
        
        promotion = PromotionService.create(
            db,
            name=payload.name,
            description=payload.description,
            code=payload.code,
            promotion_type=payload.promotion_type,
            discount_value=payload.discount_value,
            max_discount_amount=payload.max_discount_amount,
            min_purchase_amount=payload.min_purchase_amount,
            max_uses=payload.max_uses,
            max_uses_per_user=payload.max_uses_per_user,
            start_date=payload.start_date,
            end_date=payload.end_date,
            applies_to_all_events=payload.applies_to_all_events,
            applies_to_new_users_only=payload.applies_to_new_users_only,
            is_public=payload.is_public,
            created_by_id=current_user["id"],   # 🔥 lo tomamos del usuario autenticado
            event_id=payload.event_id
        )
        return promotion
    except Exception as e:
        import traceback
        print("❌ ERROR en create_promotion:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# =========================================================
# 🔹 Actualizar una promoción existente (edición completa)
# =========================================================
@router.put("/{promotion_id}", response_model=PromotionResponse)
def update_promotion(
    promotion_id: UUID,
    payload: PromotionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Actualiza los datos de una promoción.
    Campos editables:
      - name, description, code
      - promotion_type, discount_value
      - start_date, end_date
    """
    try:
        print("🛠 Payload recibido en update:", payload.dict(exclude_unset=True))

        promotion = PromotionService.update(
            db=db,
            promo_id=promotion_id,
            update_data=payload,
            current_user_id=current_user["id"]
        )
        return promotion
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print("❌ ERROR en update_promotion:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



# =========================================================
# 🔹 Eliminar una promoción
# =========================================================
@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promotion(
    promotion_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Elimina una promoción (solo si pertenece al evento del organizador).
    """
    try:
        PromotionService.delete(db, str(promotion_id))
        return {"detail": "Promoción eliminada correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
