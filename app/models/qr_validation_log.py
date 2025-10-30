from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class QRValidationLog(Base):
    __tablename__ = "qr_validation_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Log details (según diagrama)
    attemptTime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    success = Column(Boolean, nullable=False)
    ipAddress = Column(String(45), nullable=True)  # IPv6 compatible
    device = Column(String(255), nullable=True)
    
    # Foreign key
    validation_id = Column(UUID(as_uuid=True), ForeignKey("validations.id"), nullable=False)
    
    # Relationship
    validation = relationship("Validation", back_populates="validation_logs")
    
    def __repr__(self):
        return f"<QRValidationLog(validation_id='{self.validation_id}', success='{self.success}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "attemptTime": self.attemptTime.isoformat() if self.attemptTime else None,
            "success": self.success,
            "ipAddress": self.ipAddress,
            "device": self.device,
            "validationId": str(self.validation_id)
        }
