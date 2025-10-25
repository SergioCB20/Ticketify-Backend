from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class EventSchedule(Base):
    __tablename__ = "event_schedules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    dateTime = Column(DateTime(timezone=True), nullable=False)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    
    # Foreign key
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Relationship
    event = relationship("Event", back_populates="schedules")
    
    def __repr__(self):
        return f"<EventSchedule(dateTime='{self.dateTime}', duration='{self.duration}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "dateTime": self.dateTime.isoformat() if self.dateTime else None,
            "duration": self.duration,
            "eventId": str(self.event_id)
        }
