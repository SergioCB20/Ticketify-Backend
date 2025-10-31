from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.models.event import EventStatus


# ==============================
# 🧱 BASE SCHEMA
# ==============================
class EventBase(BaseModel):
    title: str = Field(..., example="Festival Tech 2025")
    description: Optional[str] = Field(None, example="Evento tecnológico con charlas y conciertos")
    startDate: datetime = Field(..., example="2025-12-10T18:00:00Z")
    endDate: datetime = Field(..., example="2025-12-11T02:00:00Z")
    venue: str = Field(..., example="Lima Convention Center")
    totalCapacity: int = Field(..., example=5000)
    status: Optional[EventStatus] = Field(default=EventStatus.DRAFT, example="PUBLISHED")
    multimedia: Optional[List[str]] = Field(default_factory=list, example=["https://cdn.ticketify.pe/img/event1.jpg"])
    categoryId: Optional[UUID] = Field(None, alias="categoryId")


# ==============================
# 🟢 CREATE & UPDATE
# ==============================
class EventCreate(EventBase):
    """Datos requeridos para crear un evento."""
    pass


class EventUpdate(BaseModel):
    """Campos opcionales para actualizar un evento."""
    title: Optional[str] = None
    description: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    venue: Optional[str] = None
    totalCapacity: Optional[int] = None
    status: Optional[EventStatus] = None
    multimedia: Optional[List[str]] = None
    categoryId: Optional[UUID] = None


# ==============================
# 🧾 RESPONSE / OUTPUT
# ==============================
class PromotionOut(BaseModel):
    """Vista simplificada de las promociones asociadas."""
    id: UUID
    name: str
    description: Optional[str]
    code: str
    discountValue: float
    startDate: datetime
    endDate: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class EventOut(BaseModel):
    """Vista detallada del evento (para respuestas API)."""
    id: UUID
    title: str
    description: Optional[str]
    startDate: datetime
    endDate: datetime
    venue: str
    totalCapacity: int
    status: EventStatus
    multimedia: Optional[List[str]]
    createdAt: datetime
    updatedAt: datetime
    organizerId: UUID
    categoryId: Optional[UUID]
    availableTickets: Optional[int]
    isSoldOut: Optional[bool]
    promotions: Optional[List[PromotionOut]] = []

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
