from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Analytics(Base):
    __tablename__ = "analytics"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Analytics data (según diagrama)
    totalSales = Column(Integer, default=0, nullable=False)
    revenue = Column(Numeric(10, 2), default=0, nullable=False)
    attendees = Column(Integer, default=0, nullable=False)
    salesByDate = Column(Text, nullable=True)  # JSON: {"2025-01-01": 10, "2025-01-02": 15}
    
    # Foreign key
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False, unique=True)
    
    # Relationship
    event = relationship("Event", back_populates="analytics")
    
    def __repr__(self):
        return f"<Analytics(event_id='{self.event_id}', totalSales='{self.totalSales}')>"
    
    def calculate_metrics(self):
        """Calculate analytics metrics"""
        # Lógica para calcular métricas del evento
        pass
    
    def track_behavior(self, behavior_data: dict):
        """Track user behavior"""
        # Lógica para trackear comportamiento
        pass
    
    def to_dict(self):
        import json
        return {
            "id": str(self.id),
            "totalSales": self.totalSales,
            "revenue": float(self.revenue) if self.revenue else 0,
            "attendees": self.attendees,
            "salesByDate": json.loads(self.salesByDate) if self.salesByDate else {},
            "eventId": str(self.event_id)
        }
