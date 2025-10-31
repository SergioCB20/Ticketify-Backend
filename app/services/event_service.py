from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.event import Event, EventStatus
from app.repositories.event_repository import EventRepository
from app.schemas.event_schema import EventCreate, EventUpdate


class EventService:
    """Servicio de negocio para manejar eventos y sus reglas."""

    @staticmethod
    def get_all_events(db: Session) -> List[Event]:
        """Obtiene todos los eventos (solo para admins o debugging)."""
        events = EventRepository.get_all(db)
        return events

    @staticmethod
    def get_event_by_id(db: Session, event_id: str) -> Event:
        """Obtiene un evento específico."""
        event = EventRepository.get_by_id(db, event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        return event

    @staticmethod
    def get_events_by_organizer(
        db: Session, organizer_id: str, include_drafts: bool = False
    ) -> List[Event]:
        """Devuelve los eventos del organizador logueado."""
        events = EventRepository.get_by_organizer(
            db=db,
            organizer_id=organizer_id,
            only_published=not include_drafts
        )
        return events

    @staticmethod
    def create_event(db: Session, event_data: EventCreate, organizer_id: str) -> Event:
        """Crea un nuevo evento con validaciones básicas."""
        # Validar que fecha de fin > fecha de inicio
        if event_data.endDate <= event_data.startDate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin debe ser posterior a la fecha de inicio"
            )

        # Crear evento
        new_event = {
            **event_data.dict(),
            "organizer_id": organizer_id,
            "status": EventStatus.DRAFT
        }
        event = EventRepository.create(db, new_event)
        return event

    @staticmethod
    def update_event(db: Session, event_id: str, updates: EventUpdate, organizer_id: str) -> Event:
        """Actualiza los datos de un evento (solo si pertenece al organizador)."""
        event = EventRepository.get_by_id(db, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        if str(event.organizer_id) != str(organizer_id):
            raise HTTPException(status_code=403, detail="No tienes permiso para editar este evento")

        if updates.endDate and updates.startDate and updates.endDate <= updates.startDate:
            raise HTTPException(status_code=400, detail="Las fechas son inválidas")

        updated = EventRepository.update(db, event_id, updates.dict(exclude_unset=True))
        return updated

    @staticmethod
    def delete_event(db: Session, event_id: str, organizer_id: str) -> bool:
        """Elimina un evento (solo si pertenece al organizador)."""
        event = EventRepository.get_by_id(db, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        if str(event.organizer_id) != str(organizer_id):
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento")

        return EventRepository.delete(db, event_id)

    @staticmethod
    def get_promotions_for_event(db: Session, event_id: str, organizer_id: str):
        """Devuelve las promociones asociadas a un evento del organizador."""
        event = EventRepository.get_by_id(db, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        if str(event.organizer_id) != str(organizer_id):
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este evento")

        promotions = EventRepository.get_promotions_by_event(db, event_id)

        serialized_promos = []
        for p in promotions:
            # ⚙️ Si es dict o Row, conviértelo en dict plano
            if isinstance(p, dict):
                serialized_promos.append(p)
            elif hasattr(p, "_asdict"):  # caso RowMapping
                serialized_promos.append(p._asdict())
            elif hasattr(p, "to_dict"):
                serialized_promos.append(p.to_dict())
            else:
                # fallback: intenta construir dict desde atributos SQLAlchemy
                try:
                    serialized_promos.append({
                        c.name: getattr(p, c.name)
                        for c in p.__table__.columns
                    })
                except Exception as e:
                    print("❌ Error serializando promoción:", e)
                    continue

        return serialized_promos

