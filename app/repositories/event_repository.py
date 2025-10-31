from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models.event import Event
import uuid

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    # Busca en la BD todos los eventos que coincidan con el ID del organizador
    async def get_events_by_organizer_id(self, organizer_id: uuid.UUID) -> list[Event]:
        stmt = select(Event).where(Event.organizer_id == organizer_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()