from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Support ticket details (según diagrama)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String(50), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="support_tickets")
    admin = relationship("User", foreign_keys=[assigned_to], back_populates="support_tickets_assigned")
    
    def __repr__(self):
        return f"<SupportTicket(subject='{self.subject}', status='{self.status}')>"
    
    def create_ticket(self):
        """Create a new support ticket"""
        self.status = "OPEN"
        self.createdAt = func.now()
    
    def update_status(self, new_status: str):
        """Update ticket status"""
        valid_statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
        if new_status in valid_statuses:
            self.status = new_status
            self.updatedAt = func.now()
    
    def add_comment(self, comment: str):
        """Add a comment to the ticket"""
        # Esta funcionalidad podría extenderse con un modelo SupportComment
        pass
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "subject": self.subject,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,
            "userId": str(self.user_id),
            "assignedTo": str(self.assigned_to) if self.assigned_to else None
        }
