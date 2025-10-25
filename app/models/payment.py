from sqlalchemy import Column, String, DateTime, Enum, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING" 
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    MERCADOPAGO = "MERCADOPAGO"
    PAYPAL = "PAYPAL"
    BANK_TRANSFER = "BANK_TRANSFER"

class Payment(Base):
    __tablename__ = "payments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Payment details (según diagrama - SIMPLIFICADO)
    amount = Column(Numeric(10, 2), nullable=False)
    paymentMethod = Column(Enum(PaymentMethod), nullable=False)
    transactionId = Column(String(255), nullable=True, index=True)  # ID de transacción externa
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    paymentDate = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    tickets = relationship("Ticket", back_populates="payment")
    transactions = relationship("Transaction", back_populates="payment")
    
    def __repr__(self):
        return f"<Payment(id='{self.id}', amount='{self.amount}', status='{self.status}')>"
    
    def process_payment(self):
        """Process payment"""
        from datetime import datetime
        self.status = PaymentStatus.PROCESSING
        # Lógica de procesamiento aquí
        self.status = PaymentStatus.COMPLETED
        self.paymentDate = datetime.utcnow()
    
    def refund_payment(self):
        """Refund payment"""
        if self.status == PaymentStatus.COMPLETED:
            self.status = PaymentStatus.REFUNDED
            return True
        return False
    
    @property
    def is_completed(self):
        """Check if payment is completed"""
        return self.status == PaymentStatus.COMPLETED
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "amount": float(self.amount) if self.amount else None,
            "paymentMethod": self.paymentMethod.value,
            "transactionId": self.transactionId,
            "status": self.status.value,
            "paymentDate": self.paymentDate.isoformat() if self.paymentDate else None,
            "userId": str(self.user_id),
            "isCompleted": self.is_completed,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }
