from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import List, Optional

from app.schemas.promotion_schema import PromotionCreate, PromotionUpdate, PromotionResponse
from app.models.promotion import PromotionStatus, Promotion
from app.models.event import Event
from app.repositories import promotion_repository
from fastapi import HTTPException, status

# -----------------------------------------------------------
# 📌 Crear una promoción asociada a un evento
# -----------------------------------------------------------
def create_promotion_service(db: Session, data: PromotionCreate, organizer_id: UUID) -> PromotionResponse:
    # 1️⃣ Validar que el evento exista
    event = db.query(Event).filter(Event.id == data.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # 2️⃣ Validar que el usuario sea el organizador del evento
    if event.organizer_id != organizer_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para agregar promociones a este evento")

    # 3️⃣ Validar fechas (la promoción debe estar dentro del rango del evento)
    if data.start_date >= data.end_date:
        raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    # 4️⃣ Crear la promoción
    new_promo = promotion_repository.create_promotion(db, data)

    return PromotionResponse.from_orm(new_promo)


# -----------------------------------------------------------
# 📌 Obtener todas las promociones de un evento
# -----------------------------------------------------------
def get_promotions_by_event_service(db: Session, event_id: UUID, organizer_id: UUID) -> List[PromotionResponse]:
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if event.organizer_id != organizer_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las promociones de este evento")

    promotions = promotion_repository.get_promotions_by_event(db, event_id)
    return [PromotionResponse.from_orm(p) for p in promotions]

def get_all_promotions_service(db: Session, organizer_id: str):
    return db.query(Promotion).filter_by(organizer_id=organizer_id).all()

# -----------------------------------------------------------
# 📌 Actualizar promoción
# -----------------------------------------------------------
def update_promotion_service(db: Session, promo_id: UUID, update_data: PromotionUpdate, organizer_id: UUID) -> PromotionResponse:
    promo = promotion_repository.get_promotion_by_id(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    # Verificar permisos
    event = promo.events[0] if promo.events else None
    if not event or event.organizer_id != organizer_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar esta promoción")

    # Validar fechas si se actualizan
    if update_data.start_date and update_data.end_date:
        if update_data.start_date >= update_data.end_date:
            raise HTTPException(status_code=400, detail="La fecha de inicio debe ser anterior a la fecha de fin")

    updated_promo = promotion_repository.update_promotion(db, promo_id, update_data)
    return PromotionResponse.from_orm(updated_promo)


# -----------------------------------------------------------
# 📌 Eliminar promoción
# -----------------------------------------------------------
def delete_promotion_service(db: Session, promo_id: UUID, organizer_id: UUID):
    promo = promotion_repository.get_promotion_by_id(db, promo_id)
    if not promo:
        raise HTTPException(status_code=404, detail="Promoción no encontrada")

    event = promo.events[0] if promo.events else None
    if not event or event.organizer_id != organizer_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar esta promoción")

    success = promotion_repository.delete_promotion(db, promo_id)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo eliminar la promoción")

    return {"message": "Promoción eliminada correctamente"}
