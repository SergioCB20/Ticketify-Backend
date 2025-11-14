from sqlalchemy import Column, String, Boolean, DateTime, Enum, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class ListingStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    RESERVED = "RESERVED"

class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Listing details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)  # For reference
    
    # Negotiation
    is_negotiable = Column(Boolean, default=False, nullable=False)
    min_price = Column(Numeric(10, 2), nullable=True)  # Minimum acceptable price
    
    # Listing status
    status = Column(Enum(ListingStatus), default=ListingStatus.ACTIVE, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    # Sales tracking
    views_count = Column(String, default="0", nullable=False)
    inquiries_count = Column(String, default="0", nullable=False)
    
    # Additional information
    seller_notes = Column(Text, nullable=True)
    transfer_method = Column(String(100), nullable=True)  # How ticket will be transferred
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    sold_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Relationships
    seller = relationship("User", foreign_keys=[seller_id], back_populates="marketplace_listings")
    buyer = relationship("User", foreign_keys=[buyer_id])
    ticket = relationship("Ticket", back_populates="marketplace_listing")
    event = relationship("Event", back_populates="marketplace_listings")
    
    def __repr__(self):
        return f"<MarketplaceListing(title='{self.title}', price='{self.price}', status='{self.status}')>"
    
    @property
    def is_active(self):
        """Check if listing is active and can be purchased"""
        from datetime import datetime
        
        if self.status != ListingStatus.ACTIVE:
            return False
            
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
            
        return True
    @property
    def ticket_type_id(self):
        return self.ticket.ticket_type.id if self.ticket and self.ticket.ticket_type else None

    @property
    def discount_percentage(self):
        """Calculate discount percentage from original price"""
        if not self.original_price or self.original_price <= 0:
            return 0
            
        discount = (float(self.original_price) - float(self.price)) / float(self.original_price)
        return max(0, discount * 100)
    
    @property
    def is_discounted(self):
        """Check if listing is discounted from original price"""
        return self.original_price and float(self.price) < float(self.original_price)
    
    def increment_views(self):
        """Increment view counter"""
        current_views = int(self.views_count or "0")
        self.views_count = str(current_views + 1)
    
    def increment_inquiries(self):
        """Increment inquiry counter"""
        current_inquiries = int(self.inquiries_count or "0")
        self.inquiries_count = str(current_inquiries + 1)
    
    def mark_as_sold(self, buyer_id: uuid.UUID):
        """Mark listing as sold"""
        from datetime import datetime
        self.status = ListingStatus.SOLD
        self.buyer_id = buyer_id
        self.sold_at = datetime.utcnow()
    
    def mark_as_expired(self):
        """Mark listing as expired"""
        self.status = ListingStatus.EXPIRED
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "originalPrice": float(self.original_price) if self.original_price else None,
            "isNegotiable": self.is_negotiable,
            "minPrice": float(self.min_price) if self.min_price else None,
            "status": self.status.value,
            "isFeatured": self.is_featured,
            "viewsCount": int(self.views_count or "0"),
            "inquiriesCount": int(self.inquiries_count or "0"),
            "sellerNotes": self.seller_notes,
            "transferMethod": self.transfer_method,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "soldAt": self.sold_at.isoformat() if self.sold_at else None,
            "sellerId": str(self.seller_id),
            "buyerId": str(self.buyer_id) if self.buyer_id else None,
            "ticketId": str(self.ticket_id),
            "eventId": str(self.event_id),
            "isActive": self.is_active,
            "discountPercentage": self.discount_percentage,
            "isDiscounted": self.is_discounted
        }
