from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

# =========================================================
# 🧩 Event Create & Update Schemas
# =========================================================
class EventCreate(BaseModel):
    """Schema for creating a new event"""
    title: str = Field(..., min_length=3, max_length=200, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    startDate: datetime = Field(..., description="Event start date and time")
    endDate: datetime = Field(..., description="Event end date and time")
    venue: str = Field(..., min_length=3, max_length=200, description="Event venue/location")
    totalCapacity: int = Field(..., gt=0, description="Total capacity of the event")
    #multimedia: Optional[List[str]] = Field(default=[], description="List of image/video URLs")
    category_id: Optional[UUID] = Field(None, description="Event category ID")

    @validator('endDate')
    def validate_end_date(cls, v, values):
        if 'startDate' in values and v <= values['startDate']:
            raise ValueError('endDate must be after startDate')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Concierto Rock en Vivo 2025",
                "description": "Las mejores bandas de rock en un solo lugar",
                "startDate": "2025-11-15T20:00:00",
                "endDate": "2025-11-15T23:00:00",
                "venue": "Estadio Nacional, Lima",
                "totalCapacity": 5000,
                #"multimedia": ["https://example.com/image1.jpg"],
                "category_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class EventUpdate(BaseModel):
    """Schema for updating an event"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    venue: Optional[str] = Field(None, min_length=3, max_length=200)
    totalCapacity: Optional[int] = Field(None, gt=0)
    #multimedia: Optional[List[str]] = None
    category_id: Optional[UUID] = None
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Concierto Rock en Vivo 2025 - ACTUALIZADO",
                "totalCapacity": 6000
            }
        }


# =========================================================
# 🧾 Event Response Schemas
# =========================================================
class EventResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    startDate: datetime
    endDate: datetime
    venue: str
    totalCapacity: int
    status: str
    photoUrl: Optional[str] = None
    availableTickets: int
    isSoldOut: bool
    organizerId: UUID
    categoryId: Optional[UUID] = None
    category: Optional[Dict[str, Any]] = None
    minPrice: Optional[float] = None
    maxPrice: Optional[float] = None
    createdAt: datetime
    updatedAt: datetime

    ticket_types: List[Any] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


# =========================================================
# 🎟️ Ticket Types Schema
# =========================================================
class TicketTypeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    quantity_available: int
    sold_quantity: int
    remaining_quantity: int
    min_purchase: int
    max_purchase: int
    is_active: bool
    is_sold_out: bool

    class Config:
        from_attributes = True


# =========================================================
# 🧾 Event Detail Schema
# =========================================================
class EventDetailResponse(EventResponse):
    """
    Respuesta detallada del evento, con tipos de tickets.
    """
    organizer: Optional[Dict[str, Any]] = None
    category: Optional[Dict[str, Any]] = None
    ticket_types: List[TicketTypeResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
        orm_mode = True


# =========================================================
# 📄 Listado / Paginación
# =========================================================
class EventListResponse(BaseModel):
    events: List[EventResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int

    class Config:
        from_attributes = True


class EventSimpleResponse(BaseModel):
    id: UUID
    title: str
    startDate: datetime
    venue: str
    photoUrl: Optional[str] = None
    #multimedia: Optional[List[str]] = None

    class Config:
        from_attributes = True


# =========================================================
# 🔍 Búsqueda avanzada
# =========================================================
class EventSearchFilters(BaseModel):
    query: Optional[str] = Field(None, description="Texto de búsqueda en título y descripción")
    categories: Optional[List[str]] = Field([], description="Lista de slugs de categorías")
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

    @validator('categories', pre=True)
    def split_categories(cls, v):
        if isinstance(v, str):
            return [c.strip() for c in v.split(',') if c.strip()]
        return v or []

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ['DRAFT', 'PUBLISHED', 'CANCELLED', 'COMPLETED']
            if v.upper() not in valid_statuses:
                raise ValueError(f"Estado debe ser uno de: {', '.join(valid_statuses)}")
            return v.upper()
        return v


class EventSearchResponse(BaseModel):
    events: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    total_pages: int

    class Config:
        from_attributes = True


# =========================================================
# 🗂️ Categorías
# =========================================================
class CategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    slug: str
    icon: Optional[str] = None
    color: Optional[str] = None
    imageUrl: Optional[str] = None
    isActive: bool
    isFeatured: bool
    eventCount: int
    sortOrder: int

    class Config:
        from_attributes = True


class EventCategoryResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    slug: str
    icon: Optional[str] = None
    color: Optional[str] = None
    imageUrl: Optional[str] = None
    metaTitle: Optional[str] = None
    metaDescription: Optional[str] = None
    parentId: Optional[UUID] = None
    sortOrder: int
    level: int
    isActive: bool
    isFeatured: bool
    eventCount: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# =========================================================
# 🧩 Genéricos del main
# =========================================================
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


class EventStatusUpdate(BaseModel):
    """Schema for updating event status"""
    status: str = Field(..., pattern="^(DRAFT|PUBLISHED|CANCELLED|COMPLETED)$")

    class Config:
        json_schema_extra = {
            "example": {"status": "PUBLISHED"}
        }

class OrganizerEventResponse(BaseModel):
    id: str
    title: str
    date: str
    location: str
    totalTickets: int
    soldTickets: int
    status: str
    imageUrl: Optional[str] = None

    model_config = {
        "from_attributes": True
    }