from sqlalchemy import Column, String, Boolean, DateTime, Integer, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class TicketType(Base):
    __tablename__ = "ticket_types"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic information
    name = Column(String(100), nullable=False)  # e.g., "General", "VIP", "Early Bird"
    description = Column(Text, nullable=True)
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)  # For discounts
    
    # Availability
    quantity_available = Column(Integer, nullable=False)
    sold_quantity = Column(Integer, default=0, nullable=False)
    min_purchase = Column(Integer, default=1, nullable=False)
    max_purchase = Column(Integer, default=10, nullable=False)
    
    # Sales period
    sale_start_date = Column(DateTime(timezone=True), nullable=True)
    sale_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    # Display order
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)
    
    # Relationships
    event = relationship("Event", back_populates="ticket_types")
    tickets = relationship("Ticket", back_populates="ticket_type")
    
    def __repr__(self):
        return f"<TicketType(name='{self.name}', price='{self.price}')>"
    
    @property
    def remaining_quantity(self):
        """Calculate remaining tickets"""
        return max(0, self.quantity_available - self.sold_quantity)
    
    @property
    def is_sold_out(self):
        """Check if ticket type is sold out"""
        return self.remaining_quantity <= 0
    
    

    @property
    def is_on_sale(self):
        """Check if ticket type is currently on sale"""
        from datetime import datetime
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
            
        if self.sale_start_date and now < self.sale_start_date:
            return False
            
        if self.sale_end_date and now > self.sale_end_date:
            return False
            
        return not self.is_sold_out
    
    @property
    def available(self):
        """Alias para la cantidad restante de tickets (usado en purchases.py)"""
        return self.remaining_quantity
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "originalPrice": float(self.original_price) if self.original_price else None,
            "quantityAvailable": self.quantity_available,
            "soldQuantity": self.sold_quantity,
            "remainingQuantity": self.remaining_quantity,
            "minPurchase": self.min_purchase,
            "maxPurchase": self.max_purchase,
            "saleStartDate": self.sale_start_date.isoformat() if self.sale_start_date else None,
            "saleEndDate": self.sale_end_date.isoformat() if self.sale_end_date else None,
            "isActive": self.is_active,
            "isFeatured": self.is_featured,
            "isSoldOut": self.is_sold_out,
            "isOnSale": self.is_on_sale,
            "sortOrder": self.sort_order,
            "eventId": str(self.event_id),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
