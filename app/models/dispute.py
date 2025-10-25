from sqlalchemy import Column, String, DateTime, Enum, Text, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class DisputeType(str, enum.Enum):
    FRAUD = "FRAUD"
    REFUND_REQUEST = "REFUND_REQUEST"
    INVALID_TICKET = "INVALID_TICKET"
    DUPLICATE_QR = "DUPLICATE_QR"
    PAYMENT_ISSUE = "PAYMENT_ISSUE"

class DisputeStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"

class Dispute(Base):
    __tablename__ = "disputes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Dispute details (según diagrama)
    type = Column(Enum(DisputeType), nullable=False)
    status = Column(Enum(DisputeStatus), default=DisputeStatus.PENDING, nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(ARRAY(String), nullable=True)  # Lista de URLs de evidencias
    adminNotes = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolvedAt = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_admin = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="disputes")
    reporter = relationship("User", foreign_keys=[reported_by], back_populates="disputes_reported")
    admin = relationship("User", foreign_keys=[assigned_admin], back_populates="disputes_assigned")
    
    def __repr__(self):
        return f"<Dispute(type='{self.type}', status='{self.status}')>"
    
    def create_dispute(self):
        """Create a new dispute"""
        self.status = DisputeStatus.PENDING
        self.createdAt = func.now()
    
    def assign_to_admin(self, admin_id: uuid.UUID):
        """Assign dispute to an admin"""
        self.assigned_admin = admin_id
        self.status = DisputeStatus.IN_REVIEW
    
    def resolve(self, resolution_text: str, status: DisputeStatus = DisputeStatus.RESOLVED):
        """Resolve the dispute"""
        from datetime import datetime
        self.resolution = resolution_text
        self.status = status
        self.resolvedAt = datetime.utcnow()
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "type": self.type.value,
            "status": self.status.value,
            "description": self.description,
            "evidence": self.evidence if self.evidence else [],
            "adminNotes": self.adminNotes,
            "resolution": self.resolution,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "resolvedAt": self.resolvedAt.isoformat() if self.resolvedAt else None,
            "ticketId": str(self.ticket_id),
            "reportedBy": str(self.reported_by),
            "assignedAdmin": str(self.assigned_admin) if self.assigned_admin else None
        }
