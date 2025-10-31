from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.promotion import Promotion, PromotionStatus, PromotionType
from app.models.event import Event
from app.repositories import promotion_repository


# =========================================================
# 🧩 PROMOTION SERVICE — Core Business Logic
# =========================================================

def create_promotion(
    db: Session,
    name: str,
    code: str,
    promotion_type: PromotionType,
    discount_value: float,
    start_date: datetime,
    end_date: datetime,
    created_by_id: UUID,
    event_id: UUID,
    description: Optional[str] = None,
    max_discount_amount: Optional[float] = None,
    min_purchase_amount: Optional[float] = None,
    max_uses: Optional[int] = None,
    max_uses_per_user: Optional[int] = None,
    applies_to_all_events: bool = False,
    applies_to_new_users_only: bool = False,
    is_public: bool = True,
):
    """
    Crear una nueva promoción asociada a un solo evento.
    """

    # 1️⃣ Validar fechas coherentes
    if end_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de fin debe ser posterior a la fecha de inicio."
        )

    # 2️⃣ Validar código único
    existing_code = db.query(Promotion).filter(Promotion.code == code).first()
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código de promoción ya existe."
        )

    # 3️⃣ Verificar que el evento exista
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento asociado no existe."
        )

    # 4️⃣ Validar solapamiento de promociones activas dentro del mismo evento
    overlapping_promo = db.query(Promotion).filter(
        Promotion.event_id == event_id,
        Promotion.start_date <= end_date,
        Promotion.end_date >= start_date,
        Promotion.status == PromotionStatus.ACTIVE
    ).first()

    if overlapping_promo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El evento ya tiene otra promoción activa ('{overlapping_promo.code}') en ese rango de fechas."
        )

    # 5️⃣ Crear la promoción
    new_promo = Promotion(
        name=name,
        description=description,
        code=code,
        promotion_type=promotion_type,
        discount_value=discount_value,
        max_discount_amount=max_discount_amount,
        min_purchase_amount=min_purchase_amount,
        max_uses=max_uses,
        max_uses_per_user=max_uses_per_user,
        start_date=start_date,
        end_date=end_date,
        applies_to_all_events=applies_to_all_events,
        applies_to_new_users_only=applies_to_new_users_only,
        is_public=is_public,
        created_by_id=created_by_id,
        event_id=event_id,
    )

    db.add(new_promo)
    db.commit()
    db.refresh(new_promo)
    return new_promo


def get_active_promotions(db: Session) -> List[Promotion]:
    """
    Retorna todas las promociones activas y vigentes (por fecha y estado).
    """
    now = datetime.now(timezone.utc)
    promotions = db.query(Promotion).filter(
        Promotion.status == PromotionStatus.ACTIVE,
        Promotion.start_date <= now,
        Promotion.end_date >= now
    ).all()
    return promotions


def get_promotion_by_code(db: Session, code: str) -> Promotion:
    """
    Buscar una promoción por su código.
    """
    promo = db.query(Promotion).filter(Promotion.code == code).first()
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe una promoción con el código '{code}'."
        )
    return promo

def get_promotions_by_event(db: Session, event_id: UUID):
    """
    Retorna todas las promociones asociadas a un evento específico.
    """
    promotions = promotion_repository.get_promotions_by_event(db, event_id)
    if not promotions:
        return []
    return promotions

def apply_promotion(db: Session, code: str, purchase_amount: float) -> float:
    """
    Aplica una promoción al monto de compra (si es válida).
    Retorna el monto descontado.
    """
    promo = get_promotion_by_code(db, code)

    if not promo.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La promoción no está activa o ya expiró."
        )

    discount = promo.calculate_discount(purchase_amount)
    if discount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La promoción no cumple las condiciones para aplicarse."
        )

    # Incrementar contador de usos
    promo.current_uses += 1
    if promo.max_uses and promo.current_uses >= promo.max_uses:
        promo.status = PromotionStatus.USED_UP

    db.add(promo)
    db.commit()

    return discount


def deactivate_promotion(db: Session, promo_id: UUID):
    """
    Desactiva manualmente una promoción.
    """
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoción no encontrada."
        )
    
    promo.status = PromotionStatus.INACTIVE
    db.add(promo)
    db.commit()
    return {"message": f"Promoción '{promo.code}' desactivada correctamente."}


def delete_promotion(db: Session, promo_id: UUID):
    """
    Eliminar una promoción permanentemente.
    """
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoción no encontrada."
        )
    db.delete(promo)
    db.commit()
    return {"message": f"Promoción '{promo.code}' eliminada correctamente."}

def update_promotion(db: Session, promo_id: UUID, update_data):
    """
    Actualiza los detalles de una promoción existente.
    """
    promo = db.query(Promotion).filter(Promotion.id == promo_id).first()
    if not promo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Promoción no encontrada."
        )

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(promo, field, value)

    promo.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(promo)
    return promo