from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class EventPromotion(Base):
    __tablename__ = "event_promotions"

    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), primary_key=True)
    promotion_id = Column(UUID(as_uuid=True), ForeignKey("promotions.id"), primary_key=True)
