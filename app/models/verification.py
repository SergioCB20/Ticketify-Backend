from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class VerificationType(str, enum.Enum):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    PASSWORD_RESET = "PASSWORD_RESET"
    PHONE_VERIFICATION = "PHONE_VERIFICATION"
    TWO_FACTOR_AUTH = "TWO_FACTOR_AUTH"
    ACCOUNT_RECOVERY = "ACCOUNT_RECOVERY"

class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"

class Verification(Base):
    __tablename__ = "verifications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Verification details
    verification_type = Column(Enum(VerificationType), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    code = Column(String(10), nullable=True)  # For SMS/phone verification
    
    # Target information
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Status and attempts
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    attempts = Column(String, default="0", nullable=False)
    max_attempts = Column(String, default="3", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    meta_data = Column(Text, nullable=True)  # JSON string for additional data
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="verifications")
    
    def __repr__(self):
        return f"<Verification(type='{self.verification_type}', status='{self.status}')>"
    
    @property
    def is_expired(self):
        """Check if verification has expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if verification is valid"""
        return (
            self.status == VerificationStatus.PENDING and 
            not self.is_expired and 
            int(self.attempts) < int(self.max_attempts)
        )
    
    @property
    def remaining_attempts(self):
        """Get remaining verification attempts"""
        return max(0, int(self.max_attempts) - int(self.attempts))
    
    def increment_attempts(self):
        """Increment attempt counter"""
        current_attempts = int(self.attempts or "0")
        self.attempts = str(current_attempts + 1)
        
        if int(self.attempts) >= int(self.max_attempts):
            self.status = VerificationStatus.FAILED
    
    def mark_as_verified(self):
        """Mark verification as completed"""
        from datetime import datetime
        self.status = VerificationStatus.VERIFIED
        self.verified_at = datetime.utcnow()
    
    def mark_as_expired(self):
        """Mark verification as expired"""
        self.status = VerificationStatus.EXPIRED
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "verificationType": self.verification_type.value,
            "token": self.token,
            "code": self.code,
            "email": self.email,
            "phone": self.phone,
            "status": self.status.value,
            "attempts": int(self.attempts or "0"),
            "maxAttempts": int(self.max_attempts or "3"),
            "remainingAttempts": self.remaining_attempts,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "verifiedAt": self.verified_at.isoformat() if self.verified_at else None,
            "meta_data": self.meta_data,
            "ipAddress": self.ip_address,
            "userAgent": self.user_agent,
            "userId": str(self.user_id),
            "isExpired": self.is_expired,
            "isValid": self.is_valid
        }
