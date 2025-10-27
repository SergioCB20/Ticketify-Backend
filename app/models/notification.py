from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class NotificationType(str, enum.Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    PURCHASE_CONFIRMATION = "PURCHASE_CONFIRMATION"
    EVENT_REMINDER = "EVENT_REMINDER"
    EVENT_CANCELLED = "EVENT_CANCELLED"
    EVENT_UPDATED = "EVENT_UPDATED"
    TICKET_TRANSFERRED = "TICKET_TRANSFERRED"
    PROMOTION_AVAILABLE = "PROMOTION_AVAILABLE"
    MARKETPLACE_SALE = "MARKETPLACE_SALE"

class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"

class Notification(Base):
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    
    # Delivery
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.IN_APP, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    
    # Scheduling
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    action_url = Column(String(500), nullable=True)  # URL for action button
    action_text = Column(String(100), nullable=True)  # Text for action button
    image_url = Column(String(500), nullable=True)
    metaData = Column(Text, nullable=True)  # JSON string for additional data - CAMBIADO de meta_data a metaData
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    event = relationship("Event")
    
    def __repr__(self):
        return f"<Notification(title='{self.title}', type='{self.notification_type}')>"
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        from datetime import datetime
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    @property
    def is_pending(self):
        """Check if notification is pending to be sent"""
        from datetime import datetime
        
        if self.is_sent:
            return False
            
        if self.scheduled_for:
            return datetime.utcnow() >= self.scheduled_for
        
        return True
    
    def mark_as_read(self):
        """Mark notification as read"""
        from datetime import datetime
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        from datetime import datetime
        self.is_sent = True
        self.sent_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "message": self.message,
            "notificationType": self.notification_type.value,
            "channel": self.channel.value,
            "isRead": self.is_read,
            "isSent": self.is_sent,
            "scheduledFor": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "sentAt": self.sent_at.isoformat() if self.sent_at else None,
            "readAt": self.read_at.isoformat() if self.read_at else None,
            "actionUrl": self.action_url,
            "actionText": self.action_text,
            "imageUrl": self.image_url,
            "metaData": self.metaData,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "userId": str(self.user_id),
            "eventId": str(self.event_id) if self.event_id else None,
            "isExpired": self.is_expired,
            "isPending": self.is_pending,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
