from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class Event(Base):
    __tablename__ = "events"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Event details
    date = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="Peru")
    
    # Capacity and pricing
    capacity = Column(Integer, nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    
    # Media
    image_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    
    # Status and visibility
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # SEO and search
    slug = Column(String(255), unique=True, index=True, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("event_categories.id"), nullable=True)
    
    # Relationships
    organizer = relationship("User", back_populates="organized_events")
    category = relationship("EventCategory", back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    purchases = relationship("Purchase", back_populates="event")
    tickets = relationship("Ticket", back_populates="event")
    marketplace_listings = relationship("MarketplaceListing", back_populates="event")
    
    def __repr__(self):
        return f"<Event(title='{self.title}', status='{self.status}')>"
    
    @property
    def available_tickets(self):
        """Calculate available tickets"""
        sold_tickets = sum(tt.sold_quantity for tt in self.ticket_types)
        return self.capacity - sold_tickets
    
    @property
    def is_sold_out(self):
        """Check if event is sold out"""
        return self.available_tickets <= 0
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "shortDescription": self.short_description,
            "date": self.date.isoformat() if self.date else None,
            "location": self.location,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "capacity": self.capacity,
            "basePrice": float(self.base_price) if self.base_price else None,
            "imageUrl": self.image_url,
            "bannerUrl": self.banner_url,
            "status": self.status.value,
            "isFeatured": self.is_featured,
            "isActive": self.is_active,
            "slug": self.slug,
            "tags": self.tags.split(",") if self.tags else [],
            "availableTickets": self.available_tickets,
            "isSoldOut": self.is_sold_out,
            "organizerId": str(self.organizer_id),
            "categoryId": str(self.category_id) if self.category_id else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "publishedAt": self.published_at.isoformat() if self.published_at else None
        }
