from sqlalchemy import Column, String, DateTime, Enum, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base


class MessageType(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"  # Mensaje a un asistente específico
    BROADCAST = "BROADCAST"  # Mensaje a todos los asistentes
    FILTERED = "FILTERED"  # Mensaje a asistentes filtrados


class EventMessage(Base):
    __tablename__ = "event_messages"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Content
    subject = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Contenido HTML del mensaje
    message_type = Column(Enum(MessageType), default=MessageType.BROADCAST, nullable=False)
    
    # Statistics
    total_recipients = Column(Integer, default=0, nullable=False)
    successful_sends = Column(Integer, default=0, nullable=False)
    failed_sends = Column(Integer, default=0, nullable=False)
    
    # Metadata
    recipient_filters = Column(Text, nullable=True)  # JSON string con filtros aplicados
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="event_messages")
    organizer = relationship("User", back_populates="sent_messages")
    
    def __repr__(self):
        return f"<EventMessage(subject='{self.subject}', type='{self.message_type}')>"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_recipients == 0:
            return 0.0
        return (self.successful_sends / self.total_recipients) * 100
    
    @property
    def is_sent(self):
        """Check if message has been sent"""
        return self.sent_at is not None
    
    def mark_as_sent(self):
        """Mark message as sent"""
        from datetime import datetime
        self.sent_at = datetime.utcnow()
    
    def update_stats(self, successful: int, failed: int):
        """Update sending statistics"""
        self.successful_sends = successful
        self.failed_sends = failed
        self.total_recipients = successful + failed
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "subject": self.subject,
            "content": self.content,
            "messageType": self.message_type.value,
            "totalRecipients": self.total_recipients,
            "successfulSends": self.successful_sends,
            "failedSends": self.failed_sends,
            "successRate": round(self.success_rate, 2),
            "recipientFilters": self.recipient_filters,
            "sentAt": self.sent_at.isoformat() if self.sent_at else None,
            "isSent": self.is_sent,
            "eventId": str(self.event_id),
            "organizerId": str(self.organizer_id),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
