from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.event import Event
from fastapi import HTTPException, status 

from app.models.promotion import Promotion, PromotionStatus


class PromotionRepository:
    """Repository for Promotion-related DB operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, promo_id: UUID) -> Optional[Promotion]:
        return self.db.query(Promotion).filter(Promotion.id == promo_id).first()

    def get_promotions_by_event(self, event_id: UUID) -> List[Promotion]:
        """Return all promotions for a given event (ordered by start_date desc)."""
        return (
            self.db.query(Promotion)
            .filter(Promotion.event_id == event_id)
            .order_by(Promotion.start_date.desc())
            .all()
        )

    def get_active(self) -> List[Promotion]:
        """Return active promotions based on status and date range."""
        now = datetime.now(timezone.utc)
        return (
            self.db.query(Promotion)
            .filter(
                Promotion.status == PromotionStatus.ACTIVE,
                Promotion.start_date <= now,
                Promotion.end_date >= now,
            )
            .all()
        )

    def create(self, promo: Promotion) -> Promotion:
        # 1️⃣ Validar fechas coherentes
        if promo.end_date <= promo.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin debe ser posterior a la fecha de inicio."
            )

        # 2️⃣ Validar código único
        existing_code = self.db.query(Promotion).filter(Promotion.code == promo.code).first()
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código de promoción ya existe."
            )

        # 3️⃣ Verificar que el evento exista
        event = self.db.query(Event).filter(Event.id == promo.event_id).first()
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El evento asociado no existe."
            )

        # 4️⃣ Validar solapamiento de promociones activas dentro del mismo evento
        overlapping_promo = self.db.query(Promotion).filter(
            Promotion.event_id == promo.event_id,
            Promotion.start_date <= promo.end_date,
            Promotion.end_date >= promo.start_date,
            Promotion.status == PromotionStatus.ACTIVE
        ).first()

        if overlapping_promo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El evento ya tiene otra promoción activa ('{overlapping_promo.code}') en ese rango de fechas."
            )
        self.db.add(promo)
        self.db.commit()
        self.db.refresh(promo)
        return promo

    def update(self, promo_id: UUID, updates: dict) -> Optional[Promotion]:
        promo = self.get_by_id(promo_id)
        if not promo:
            return None

        for k, v in updates.items():
            if hasattr(promo, k):
                setattr(promo, k, v)

        self.db.commit()
        self.db.refresh(promo)
        return promo

    def delete(self, promo_id: UUID) -> bool:
        promo = self.get_by_id(promo_id)
        if not promo:
            return False
        self.db.delete(promo)
        self.db.commit()
        return True

