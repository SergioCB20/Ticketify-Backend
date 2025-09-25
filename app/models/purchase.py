from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class PurchaseStatus(str, enum.Enum):
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

class Purchase(Base):
    __tablename__ = "purchases"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Purchase details
    total_amount = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0, nullable=False)
    service_fee = Column(Numeric(10, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)
    
    # Quantity and pricing
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    
    # Status and payment
    status = Column(Enum(PurchaseStatus), default=PurchaseStatus.PENDING, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_reference = Column(String(255), nullable=True)  # External payment ID
    
    # Buyer information
    buyer_email = Column(String(255), nullable=False)
    buyer_phone = Column(String(20), nullable=True)
    buyer_document = Column(String(20), nullable=True)
    
    # Billing information
    billing_name = Column(String(200), nullable=True)
    billing_address = Column(Text, nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_country = Column(String(100), nullable=True)
    
    # Processing dates
    purchase_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    confirmation_date = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    refund_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    promotion_id = Column(UUID(as_uuid=True), ForeignKey("promotions.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="purchases")
    event = relationship("Event", back_populates="purchases")
    ticket_type = relationship("TicketType")
    promotion = relationship("Promotion", back_populates="purchases")
    tickets = relationship("Ticket", back_populates="purchase", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Purchase(id='{self.id}', status='{self.status}', total='{self.total_amount}')>"
    
    @property
    def is_completed(self):
        """Check if purchase is completed"""
        return self.status == PurchaseStatus.COMPLETED
    
    @property
    def can_be_cancelled(self):
        """Check if purchase can be cancelled"""
        return self.status in [PurchaseStatus.PENDING, PurchaseStatus.PROCESSING]
    
    @property
    def can_be_refunded(self):
        """Check if purchase can be refunded"""
        return self.status == PurchaseStatus.COMPLETED
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "totalAmount": float(self.total_amount) if self.total_amount else None,
            "subtotal": float(self.subtotal) if self.subtotal else None,
            "taxAmount": float(self.tax_amount) if self.tax_amount else None,
            "serviceFee": float(self.service_fee) if self.service_fee else None,
            "discountAmount": float(self.discount_amount) if self.discount_amount else None,
            "quantity": self.quantity,
            "unitPrice": float(self.unit_price) if self.unit_price else None,
            "status": self.status.value,
            "paymentMethod": self.payment_method.value if self.payment_method else None,
            "paymentReference": self.payment_reference,
            "buyerEmail": self.buyer_email,
            "buyerPhone": self.buyer_phone,
            "buyerDocument": self.buyer_document,
            "billingName": self.billing_name,
            "billingAddress": self.billing_address,
            "billingCity": self.billing_city,
            "billingCountry": self.billing_country,
            "purchaseDate": self.purchase_date.isoformat() if self.purchase_date else None,
            "paymentDate": self.payment_date.isoformat() if self.payment_date else None,
            "confirmationDate": self.confirmation_date.isoformat() if self.confirmation_date else None,
            "notes": self.notes,
            "refundReason": self.refund_reason,
            "userId": str(self.user_id),
            "eventId": str(self.event_id),
            "ticketTypeId": str(self.ticket_type_id),
            "promotionId": str(self.promotion_id) if self.promotion_id else None,
            "isCompleted": self.is_completed,
            "canBeCancelled": self.can_be_cancelled,
            "canBeRefunded": self.can_be_refunded,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
