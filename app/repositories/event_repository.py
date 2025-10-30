# app/repositories/event_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models.event import Event  # Importa el modelo de la BD
import uuid

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_events_by_organizer_id(self, organizer_id: uuid.UUID) -> list[Event]:
        # Crea una consulta SQL: SELECT * FROM events WHERE organizer_id = :organizer_id
        stmt = select(Event).where(Event.organizer_id == organizer_id)
        
        # Ejecuta la consulta
        result = await self.db.execute(stmt)
        
        # Devuelve todos los eventos encontrados
        return result.scalars().all()