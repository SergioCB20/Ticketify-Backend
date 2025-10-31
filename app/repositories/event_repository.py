from sqlalchemy.orm import Session
from sqlalchemy.future import select
from app.models.event import Event
import uuid

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_events_by_organizer_id(self, organizer_id: uuid.UUID) -> list[Event]:
        stmt = select(Event).where(Event.organizer_id == organizer_id)
        result = self.db.execute(stmt)
        return result.scalars().all()
