from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.event import EventStatus

# ============= BASE SCHEMAS =============

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    startDate: datetime
    endDate: datetime
    venue: str = Field(..., min_length=1, max_length=200)
    totalCapacity: int = Field(..., gt=0)
    multimedia: Optional[List[str]] = Field(default_factory=list)
    category_id: Optional[UUID] = None

    @validator('endDate')
    def validate_end_date(cls, v, values):
        if 'startDate' in values and v < values['startDate']:
            raise ValueError('endDate must be after startDate')
        return v

# ============= CREATE SCHEMAS =============

class EventCreate(EventBase):
    """Schema para crear un evento"""
    pass

# ============= UPDATE SCHEMAS =============

class EventUpdate(BaseModel):
    """Schema para actualizar un evento (todos los campos opcionales)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    venue: Optional[str] = Field(None, min_length=1, max_length=200)
    totalCapacity: Optional[int] = Field(None, gt=0)
    multimedia: Optional[List[str]] = None
    category_id: Optional[UUID] = None
    status: Optional[EventStatus] = None

    @validator('endDate')
    def validate_end_date(cls, v, values):
        if v and 'startDate' in values and values['startDate'] and v < values['startDate']:
            raise ValueError('endDate must be after startDate')
        return v

# ============= RESPONSE SCHEMAS =============

class OrganizerInfo(BaseModel):
    """Información básica del organizador"""
    id: UUID
    firstName: str
    lastName: str
    email: str
    
    class Config:
        from_attributes = True

class CategoryInfo(BaseModel):
    """Información básica de la categoría"""
    id: UUID
    name: str
    
    class Config:
        from_attributes = True

class EventResponse(BaseModel):
    """Schema de respuesta básico para eventos"""
    id: UUID
    title: str
    description: Optional[str]
    startDate: datetime
    endDate: datetime
    venue: str
    totalCapacity: int
    status: EventStatus
    multimedia: List[str]
    organizerId: Optional[UUID] = Field(None, alias="organizer_id")
    categoryId: Optional[UUID]  = Field(None, alias="category_id")
    availableTickets: int=0
    isSoldOut: bool=False
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        orm_mode = True                             # Pydantic v1
        from_attributes = True                      # Pydantic v2
        allow_population_by_field_name = True

class EventDetailResponse(EventResponse):
    """Schema de respuesta detallado que incluye info del organizador y categoría"""
    organizer: Optional[OrganizerInfo] = None
    category: Optional[CategoryInfo] = None
    
    class Config:
        orm_mode = True
        from_attributes = True
        allow_population_by_field_name = True

class EventListResponse(BaseModel):
    """Schema de respuesta para lista de eventos paginada"""
    events: List[EventResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int
