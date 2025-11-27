from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Text, ForeignKey, ARRAY, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base


# =========================================================
# 🧩 Enum de Estado
# =========================================================
class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


# =========================================================
# 🧾 Modelo de Evento
# =========================================================
class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Fechas
    startDate = Column(DateTime(timezone=True), nullable=False)
    endDate = Column(DateTime(timezone=True), nullable=False)

    # Ubicación y capacidad
    venue = Column(String(200), nullable=False)
    totalCapacity = Column(Integer, nullable=False)

    # Estado
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT, nullable=False)

    # Multimedia (HEAD)
   # multimedia = Column(ARRAY(String), nullable=True)
    # Imagen binaria (MAIN)
    photo = Column(LargeBinary, nullable=True)
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Foreign keys
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("event_categories.id"), nullable=True)

    # Relaciones
    organizer = relationship("User", back_populates="organized_events")
    category = relationship("EventCategory", back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan", lazy="joined")
    tickets = relationship("Ticket", back_populates="event")
    marketplace_listings = relationship("MarketplaceListing", back_populates="event")
    notifications = relationship("Notification", back_populates="event")
    schedules = relationship("EventSchedule", back_populates="event", cascade="all, delete-orphan")
    analytics = relationship("Analytics", back_populates="event", uselist=False)
    purchases = relationship("Purchase", back_populates="event")
    promotions = relationship("Promotion", back_populates="event", cascade="all, delete-orphan", passive_deletes=True)

    # =========================================================
    # 🔹 Métodos utilitarios
    # =========================================================
    def __repr__(self):
        return f"<Event(title='{self.title}', status='{self.status}')>"

    def create_event(self):
        self.status = EventStatus.DRAFT
        self.createdAt = func.now()

    def update_event(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updatedAt = func.now()

    def cancel_event(self):
        self.status = EventStatus.CANCELLED
        self.updatedAt = func.now()

    def publish_event(self):
        self.status = EventStatus.PUBLISHED
        self.updatedAt = func.now()

    # =========================================================
    # 🔹 Propiedades Calculadas
    # =========================================================
    @property
    def available_tickets(self):
        """Entradas disponibles totales"""
        if not self.ticket_types:
            return self.totalCapacity
        sold_tickets = sum(tt.sold_quantity or 0 for tt in self.ticket_types)
        return max(self.totalCapacity - sold_tickets, 0)

    @property
    def is_sold_out(self):
        """¿El evento está agotado?"""
        return self.available_tickets <= 0

    @property
    def min_price(self):
        if not self.ticket_types:
            return None
        return min((float(tt.price) for tt in self.ticket_types if tt.is_active), default=None)

    @property
    def max_price(self):
        if not self.ticket_types:
            return None
        return max((float(tt.price) for tt in self.ticket_types if tt.is_active), default=None)

    # =========================================================
    # 🔹 Serialización
    # =========================================================
    def to_dict(self):
        """Convierte el evento en un diccionario serializable para la API"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "startDate": self.startDate.isoformat() if self.startDate else None,
            "endDate": self.endDate.isoformat() if self.endDate else None,
            "venue": self.venue,
            "totalCapacity": self.totalCapacity,
            "status": self.status.value if hasattr(self.status, "value") else self.status,
            "photoUrl": f"/api/events/{self.id}/photo" if self.photo else None,
            #"multimedia": self.multimedia or [],
            "availableTickets": self.available_tickets,
            "isSoldOut": self.is_sold_out,
            "organizerId": str(self.organizer_id) if self.organizer_id else None,
            "categoryId": str(self.category_id) if self.category_id else None,
            "category": self.category.to_dict() if hasattr(self.category, "to_dict") else None,
            "minPrice": self.min_price,
            "maxPrice": self.max_price,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None,

            # 🎟️ Incluye los tipos de ticket
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
