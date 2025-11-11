from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Text, ForeignKey, ARRAY
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
    multimedia = Column(ARRAY(String), nullable=True)  # Lista de URLs de imágenes/videos
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("event_categories.id"), nullable=True)
    
    # Relationships
    organizer = relationship("User", back_populates="organized_events")
    category = relationship("EventCategory", back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan", lazy="joined")
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
            "status": self.status.value if hasattr(self.status, "value") else self.status,
            "multimedia": self.multimedia or [],
            "availableTickets": sum(
                tt.remaining_quantity for tt in self.ticket_types if tt.is_active
            ),
            "isSoldOut": all(tt.is_sold_out for tt in self.ticket_types),
            "organizerId": str(self.organizer_id) if self.organizer_id else None,
            "categoryId": str(self.category_id) if self.category_id else None,
            "category": self.category.to_dict() if self.category else None,
            "minPrice": min((float(tt.price) for tt in self.ticket_types if tt.is_active), default=0),
            "maxPrice": max((float(tt.price) for tt in self.ticket_types if tt.is_active), default=0),
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,

            # 👇 NUEVO: incluir lista de tipos de tickets
            "ticket_types": [
                {
                    "id": str(tt.id),
                    "name": tt.name,
                    "description": tt.description,
                    "price": float(tt.price) if tt.price else None,
                    "original_price": float(tt.original_price) if tt.original_price else None,
                    "quantity_available": tt.quantity_available,
                    "sold_quantity": tt.sold_quantity,
                    "remaining_quantity": (
                        tt.remaining_quantity if hasattr(tt, "remaining_quantity") else
                        (tt.quantity_available - tt.sold_quantity)
                    ),
                    "min_purchase": tt.min_purchase,
                    "max_purchase": tt.max_purchase,
                    "is_active": tt.is_active,
                    "is_sold_out": (
                        tt.is_sold_out if hasattr(tt, "is_sold_out") else
                        (tt.sold_quantity >= tt.quantity_available)
                    ),
                }
                for tt in self.ticket_types if tt is not None
            ],
        }
