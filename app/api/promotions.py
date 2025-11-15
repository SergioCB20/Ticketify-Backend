from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.promotion import PromotionResponse, PromotionCreate, PromotionUpdate
from app.services.promotion_service import PromotionService
from app.core.dependencies import get_current_user
from app.core.database import get_db
from datetime import datetime, timezone
from app.models.promotion import Promotion

router = APIRouter(prefix="/promotions", tags=["Promotions"])

def get_event_service(db: Session = Depends(get_db)) -> PromotionService:
    """Dependencia para inyectar la capa de servicio de eventos"""
    return PromotionService(db)

@router.get("/validate", tags=["Promotions"], include_in_schema=True, dependencies=[])
def validate_promotion(
    code: str = Query(..., description="Código de promoción"),
    event_id: UUID = Query(..., description="ID del evento"),
    db: Session = Depends(get_db)
):
    """
    ✅ Endpoint público para validar códigos promocionales
    (no requiere autenticación)
    """

    promo = db.query(Promotion).filter(
        Promotion.code == code,
        Promotion.start_date <= datetime.utcnow(),
        Promotion.end_date >= datetime.utcnow(),
    ).first()

    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Código inválido o expirado"
        )

    if promo.event_id and str(promo.event_id) != str(event_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código no aplica a este evento"
        )

    return {
        "id": str(promo.id),
        "code": promo.code,
        "promotion_type": promo.promotion_type,
        "discount_value": float(promo.discount_value),
        "max_discount_amount": float(promo.max_discount_amount or 0),
        "min_purchase_amount": float(promo.min_purchase_amount or 0),
        "start_date": promo.start_date,
        "end_date": promo.end_date,
    }


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
    promotion_service: PromotionService = Depends(get_event_service),
    current_user=Depends(get_current_user)
):
    """
    Crea una nueva promoción asociada a un evento.
    """
    try:
        print("📦 Payload recibido en FastAPI:", payload)
        print("📦 Payload dict():", payload.dict())  # 👈 añade esta línea
        
        promotion = promotion_service.create(
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
            created_by_id=payload.created_by_id,
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
            current_user_id=current_user.id
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


# =========================================================
# 🔹 Obtener promociones por evento
# =========================================================
@router.get("/events/{event_id}", response_model=List[PromotionResponse])
def get_promotions_by_event(
    event_id: UUID,
    promotion_service: PromotionService = Depends(get_event_service),
    current_user=Depends(get_current_user)
):
    """
    Retorna las promociones asociadas a un evento específico.
    Simplemente delega en PromotionService.get_by_event y devuelve lo que ese método retorne.
    """
    try:
        promotions = promotion_service.get_by_event(event_id)
        return promotions or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



