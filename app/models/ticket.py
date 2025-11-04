from sqlalchemy import Column, String, Boolean, DateTime, Enum, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class TicketStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    USED = "USED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    TRANSFERRED = "TRANSFERRED"

class Ticket(Base):
    __tablename__ = "tickets"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Ticket details (según diagrama - SIMPLIFICADO)
    price = Column(Numeric(10, 2), nullable=False)
    qrCode = Column(String, nullable=True)
    purchaseDate = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.ACTIVE, nullable=False)
    isValid = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"), nullable=False)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    event = relationship("Event", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    payment = relationship("Payment", back_populates="tickets")
    purchase = relationship("Purchase", back_populates="tickets")
    marketplace_listing = relationship("MarketplaceListing", back_populates="ticket", uselist=False)
    validations = relationship("Validation", back_populates="ticket")
    transfers = relationship("TicketTransfer", foreign_keys="TicketTransfer.ticket_id", back_populates="ticket")
    disputes = relationship("Dispute", back_populates="ticket")
    
    def __repr__(self):
        return f"<Ticket(id='{self.id}', status='{self.status}')>"
    
    def generate_qr(self):
        """Generate QR code for ticket"""
        import secrets
        self.qrCode = secrets.token_urlsafe(32)
        return self.qrCode
    
    def invalidate_qr(self):
        """Invalidate QR code"""
        self.isValid = False
        self.status = TicketStatus.CANCELLED
    
    def validate_ticket(self):
        """Validate ticket for entry"""
        if self.status == TicketStatus.ACTIVE and self.isValid:
            self.status = TicketStatus.USED
            return True
        return False
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "price": float(self.price) if self.price else None,
            "qrCode": self.qrCode,
            "purchaseDate": self.purchaseDate.isoformat() if self.purchaseDate else None,
            "status": self.status.value,
            "isValid": self.isValid,
            "userId": str(self.user_id),
            "eventId": str(self.event_id),
            "ticketTypeId": str(self.ticket_type_id),
            "paymentId": str(self.payment_id),
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }
