from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Validation(Base):
    __tablename__ = "validations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Validation details (según diagrama)
    scanTime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    scannedBy = Column(String(255), nullable=False)
    isValid = Column(Boolean, nullable=False)
    location = Column(String(255), nullable=True)
    
    # Foreign key
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="validations")
    validation_logs = relationship("QRValidationLog", back_populates="validation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Validation(ticket_id='{self.ticket_id}', isValid='{self.isValid}')>"
    
    def validate_entry(self):
        """Validate ticket entry"""
        if self.ticket.isValid and self.ticket.status.value == "ACTIVE":
            self.isValid = True
            self.ticket.status = "USED"
            return True
        self.isValid = False
        return False
    
    def log_validation(self, success: bool, ip_address: str = None, device: str = None):
        """Log validation attempt"""
        from app.models.qr_validation_log import QRValidationLog
        log = QRValidationLog(
            validation_id=self.id,
            success=success,
            ipAddress=ip_address,
            device=device
        )
        return log
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "scanTime": self.scanTime.isoformat() if self.scanTime else None,
            "scannedBy": self.scannedBy,
            "isValid": self.isValid,
            "location": self.location,
            "ticketId": str(self.ticket_id)
        }
