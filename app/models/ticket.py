from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Text, ForeignKey
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
    
    # Ticket identification
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    qr_code = Column(Text, nullable=True)  # QR code data
    barcode = Column(String(100), nullable=True)
    
    # Ticket details
    seat_number = Column(String(20), nullable=True)
    section = Column(String(50), nullable=True)
    row_number = Column(String(10), nullable=True)
    
    # Status and validation
    status = Column(Enum(TicketStatus), default=TicketStatus.ACTIVE, nullable=False)
    is_transferable = Column(Boolean, default=True, nullable=False)
    is_refundable = Column(Boolean, default=True, nullable=False)
    
    # Usage tracking
    used_at = Column(DateTime(timezone=True), nullable=True)
    validated_by = Column(String(255), nullable=True)  # Staff member who validated
    entry_gate = Column(String(50), nullable=True)
    
    # Transfer tracking
    original_owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    transferred_at = Column(DateTime(timezone=True), nullable=True)
    transfer_reason = Column(Text, nullable=True)
    
    # Additional information
    notes = Column(Text, nullable=True)
    special_requirements = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    ticket_type_id = Column(UUID(as_uuid=True), ForeignKey("ticket_types.id"), nullable=False)
    purchase_id = Column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    original_owner = relationship("User", foreign_keys=[original_owner_id])
    event = relationship("Event", back_populates="tickets")
    ticket_type = relationship("TicketType", back_populates="tickets")
    purchase = relationship("Purchase", back_populates="tickets")
    marketplace_listing = relationship("MarketplaceListing", back_populates="ticket", uselist=False)
    
    def __repr__(self):
        return f"<Ticket(number='{self.ticket_number}', status='{self.status}')>"
    
    @property
    def is_valid(self):
        """Check if ticket is valid for use"""
        from datetime import datetime
        
        if self.status != TicketStatus.ACTIVE:
            return False
            
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
            
        return True
    
    @property
    def can_be_transferred(self):
        """Check if ticket can be transferred"""
        return (
            self.is_transferable and 
            self.status == TicketStatus.ACTIVE and 
            self.is_valid
        )
    
    @property
    def can_be_refunded(self):
        """Check if ticket can be refunded"""
        return (
            self.is_refundable and 
            self.status == TicketStatus.ACTIVE and
            self.used_at is None
        )
    
    def generate_ticket_number(self):
        """Generate unique ticket number"""
        import random
        import string
        
        prefix = "TK"
        suffix = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{suffix}"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "ticketNumber": self.ticket_number,
            "qrCode": self.qr_code,
            "barcode": self.barcode,
            "seatNumber": self.seat_number,
            "section": self.section,
            "rowNumber": self.row_number,
            "status": self.status.value,
            "isTransferable": self.is_transferable,
            "isRefundable": self.is_refundable,
            "usedAt": self.used_at.isoformat() if self.used_at else None,
            "validatedBy": self.validated_by,
            "entryGate": self.entry_gate,
            "transferredAt": self.transferred_at.isoformat() if self.transferred_at else None,
            "transferReason": self.transfer_reason,
            "notes": self.notes,
            "specialRequirements": self.special_requirements,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "userId": str(self.user_id),
            "originalOwnerId": str(self.original_owner_id) if self.original_owner_id else None,
            "eventId": str(self.event_id),
            "ticketTypeId": str(self.ticket_type_id),
            "purchaseId": str(self.purchase_id),
            "isValid": self.is_valid,
            "canBeTransferred": self.can_be_transferred,
            "canBeRefunded": self.can_be_refunded,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
