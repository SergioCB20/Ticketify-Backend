from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from app.models.event import Event, EventStatus
from app.models.promotion import Promotion


class EventRepository:
    """Repositorio para operaciones CRUD de eventos."""

    @staticmethod
    def get_all(db: Session) -> List[Event]:
        """Obtiene todos los eventos (solo para admin)."""
        return db.query(Event).all()

    @staticmethod
    def get_by_id(db: Session, event_id: str) -> Optional[Event]:
        """Obtiene un evento por su ID."""
        return db.query(Event).filter(Event.id == event_id).first()

    @staticmethod
    def get_by_organizer(db: Session, organizer_id: str, only_published: bool = True) -> List[Event]:
        """
        Obtiene todos los eventos creados por un organizador.
        Si `only_published` es True, devuelve solo los eventos publicados.
        """
        query = db.query(Event).filter(Event.organizer_id == organizer_id)
        if only_published:
            query = query.filter(Event.status == EventStatus.PUBLISHED)
        return query.order_by(Event.startDate.asc()).all()

    @staticmethod
    def create(db: Session, event_data: dict) -> Event:
        """Crea un nuevo evento."""
        event = Event(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update(db: Session, event_id: str, updates: dict) -> Optional[Event]:
        """Actualiza un evento existente."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None
        for key, value in updates.items():
            if hasattr(event, key):
                setattr(event, key, value)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete(db: Session, event_id: str) -> bool:
        """Elimina un evento."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return False
        db.delete(event)
        db.commit()
        return True

    # ✅ NUEVO: obtener promociones asociadas
    @staticmethod
    def get_promotions_by_event(db: Session, event_id: str) -> List[Promotion]:
        """Devuelve todas las promociones de un evento."""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return []
        return event.promotions


# ✅ Funciones helpers (opcional, para uso directo si no usas clase)
def get_events_by_user(db: Session, user_id: str) -> List[Event]:
    """Retorna eventos activos de un organizador."""
    return db.query(Event).filter(
        Event.organizer_id == user_id,
        Event.status == EventStatus.PUBLISHED
    ).order_by(Event.startDate.asc()).all()
