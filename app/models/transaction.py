from sqlalchemy import Column, String, DateTime, Enum, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class TransactionType(str, enum.Enum):
    SALE = "SALE"
    REFUND = "REFUND"
    TRANSFER = "TRANSFER"
    COMMISSION = "COMMISSION"

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Transaction(Base):
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Transaction details (según diagrama)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    commission = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Foreign keys
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    payment = relationship("Payment", back_populates="transactions")
    user = relationship("User", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(type='{self.type}', amount='{self.amount}', status='{self.status}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "type": self.type.value,
            "amount": float(self.amount) if self.amount else None,
            "commission": float(self.commission) if self.commission else None,
            "status": self.status.value,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "paymentId": str(self.payment_id) if self.payment_id else None,
            "userId": str(self.user_id)
        }
