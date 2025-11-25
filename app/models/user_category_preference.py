from sqlalchemy import Column, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class UserCategoryPreference(Base):
    __tablename__ = "user_category_preferences"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('event_categories.id', ondelete='CASCADE'), nullable=False, index=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)  # Permite desuscribir sin borrar

    # Notification control
    last_notification_sent_at = Column(DateTime(timezone=True), nullable=True)  # Evitar spam

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="category_preferences")
    category = relationship("EventCategory", back_populates="user_preferences")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'category_id', name='uq_user_category'),
    )

    def __repr__(self):
        return f"<UserCategoryPreference(user_id='{self.user_id}', category_id='{self.category_id}', is_active={self.is_active})>"

    def to_dict(self):
        return {
            "id": str(self.id),
            "userId": str(self.user_id),
            "categoryId": str(self.category_id),
            "isActive": self.is_active,
            "lastNotificationSentAt": self.last_notification_sent_at.isoformat() if self.last_notification_sent_at else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
