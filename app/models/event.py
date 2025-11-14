from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Text, ForeignKey, ARRAY, LargeBinary
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
    
    # Basic information (según diagrama)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Event timing (ACTUALIZADO según diagrama)
    startDate = Column(DateTime(timezone=True), nullable=False)  # Cambio de 'date'
    endDate = Column(DateTime(timezone=True), nullable=False)  # NUEVO
    
    # Location (según diagrama)
    venue = Column(String(200), nullable=False)  # Renombrado de 'location'
    
    # Capacity (según diagrama)
    totalCapacity = Column(Integer, nullable=False)  # Renombrado de 'capacity'
    
    # Status
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    
    # Multimedia (NUEVO según diagrama)
    photo = Column(LargeBinary, nullable=True)  # Lista de URLs de imágenes/videos
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("event_categories.id"), nullable=True)
    
    # Relationships
    organizer = relationship("User", back_populates="organized_events")
    category = relationship("EventCategory", back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="event")
    marketplace_listings = relationship("MarketplaceListing", back_populates="event")
    notifications = relationship("Notification", back_populates="event")
    schedules = relationship("EventSchedule", back_populates="event", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="event", uselist=False)
    purchases = relationship("Purchase", back_populates="event")
    promotions = relationship("Promotion", back_populates="event")
    
    def __repr__(self):
        return f"<Event(title='{self.title}', status='{self.status}')>"
    
    def create_event(self):
        """Create new event"""
        self.status = EventStatus.DRAFT
        self.createdAt = func.now()
    
    def update_event(self, **kwargs):
        """Update event details"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updatedAt = func.now()
    
    def cancel_event(self):
        """Cancel event"""
        self.status = EventStatus.CANCELLED
        self.updatedAt = func.now()
    
    def publish_event(self):
        """Publish event"""
        self.status = EventStatus.PUBLISHED
        self.updatedAt = func.now()
    
    @property
    def available_tickets(self):
        """Calculate available tickets"""
        sold_tickets = sum(tt.sold_quantity for tt in self.ticket_types)
        return self.totalCapacity - sold_tickets
    
    @property
    def is_sold_out(self):
        """Check if event is sold out"""
        return self.available_tickets <= 0
    
    @property
    def min_price(self):
        """Get minimum ticket price"""
        if not self.ticket_types:
            return None
        return min(tt.price for tt in self.ticket_types)
    
    @property
    def max_price(self):
        """Get maximum ticket price"""
        if not self.ticket_types:
            return None
        return max(tt.price for tt in self.ticket_types)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "startDate": self.startDate.isoformat() if self.startDate else None,
            "endDate": self.endDate.isoformat() if self.endDate else None,
            "venue": self.venue,
            "totalCapacity": self.totalCapacity,
            "status": self.status.value,
            "photoUrl": f"/events/{self.id}/photo" if self.photo else None,
            "availableTickets": self.available_tickets,
            "isSoldOut": self.is_sold_out,
            "minPrice": self.min_price,
            "maxPrice": self.max_price,
            "organizerId": str(self.organizer_id),
            "categoryId": str(self.category_id) if self.category_id else None,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }
