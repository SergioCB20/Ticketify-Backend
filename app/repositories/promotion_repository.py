from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.models.promotion import Promotion
from app.models.event import Event
from app.models.event_promotion import EventPromotion
from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate
from datetime import datetime

# -------------------------------------------------------------------
# 📌 Crear promoción
# -------------------------------------------------------------------
def create_promotion(db: Session, promotion_data: PromotionCreate) -> Promotion:
    new_promo = Promotion(
        name=promotion_data.name,
        description=promotion_data.description,
        code=promotion_data.code,
        promotion_type=promotion_data.promotion_type,
        discount_value=promotion_data.discount_value,
        max_discount_amount=promotion_data.max_discount_amount,
        min_purchase_amount=promotion_data.min_purchase_amount,
        max_uses=promotion_data.max_uses,
        max_uses_per_user=promotion_data.max_uses_per_user,
        start_date=promotion_data.start_date,
        end_date=promotion_data.end_date,
        applies_to_new_users_only=promotion_data.applies_to_new_users_only,
        is_public=promotion_data.is_public,
        created_by_id=promotion_data.created_by_id
    )

    # Guardar la promoción
    db.add(new_promo)
    db.commit()
    db.refresh(new_promo)

    # Asociar al evento
    event = db.query(Event).filter(Event.id == promotion_data.event_id).first()
    if event:
        link = EventPromotion(event_id=event.id, promotion_id=new_promo.id)
        db.add(link)
        db.commit()

    db.refresh(new_promo)
    return new_promo


# -------------------------------------------------------------------
# 📌 Obtener todas las promociones de un evento
# -------------------------------------------------------------------
def get_promotions_by_event(db: Session, event_id: UUID) -> List[Promotion]:
    promotions = (
        db.query(Promotion)
        .join(EventPromotion, Promotion.id == EventPromotion.promotion_id)
        .filter(EventPromotion.event_id == event_id)
        .all()
    )
    return promotions


# -------------------------------------------------------------------
# 📌 Obtener una promoción específica
# -------------------------------------------------------------------
def get_promotion_by_id(db: Session, promo_id: UUID) -> Optional[Promotion]:
    return db.query(Promotion).filter(Promotion.id == promo_id).first()


# -------------------------------------------------------------------
# 📌 Actualizar promoción
# -------------------------------------------------------------------
def update_promotion(db: Session, promo_id: UUID, update_data: PromotionUpdate) -> Optional[Promotion]:
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        return None

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(promo, field, value)

    promo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(promo)
    return promo


# -------------------------------------------------------------------
# 📌 Eliminar promoción
# -------------------------------------------------------------------
def delete_promotion(db: Session, promo_id: UUID) -> bool:
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        return False

    db.delete(promo)
    db.commit()
    return True
