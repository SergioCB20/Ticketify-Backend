from pydantic import BaseModel, Field, validator
from pydantic import ConfigDict
from typing import Optional, List, Dict, Any
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
    id: UUID
    title: str
    description: Optional[str] = None
    startDate: datetime
    endDate: datetime
    venue: str
    totalCapacity: int
    status: str
    multimedia: Optional[List[str]] = []
    availableTickets: int
    isSoldOut: bool
    organizerId: UUID
    categoryId: Optional[UUID] = None
    category: Optional[Dict[str, Any]] = None
    minPrice: Optional[float] = None
    maxPrice: Optional[float] = None
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True

class EventListResponse(BaseModel):
    """Schema de respuesta para lista de eventos paginada"""
    events: List[EventResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int

class EventSimpleResponse(BaseModel):
    id: UUID
    title: str
    startDate: datetime 
    venue: str
    multimedia: Optional[List[str]] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class EventSearchFilters(BaseModel):
    """
    Modelo para validar los filtros de búsqueda de eventos
    """
    query: Optional[str] = Field(None, description="Texto de búsqueda en título y descripción")
    categories: Optional[List[str]] = Field([], description="Lista de slugs de categorías")
    min_price: Optional[float] = Field(None, ge=0, description="Precio mínimo de tickets")
    max_price: Optional[float] = Field(None, ge=0, description="Precio máximo de tickets")
    start_date: Optional[str] = Field(None, description="Fecha de inicio (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Fecha de fin (YYYY-MM-DD)")
    location: Optional[str] = Field(None, description="Ubicación (ciudad o lugar)")
    status: Optional[str] = Field(None, description="Estado del evento")
    
    @validator('categories', pre=True)
    def split_categories(cls, v):
        """Convertir string separado por comas en lista"""
        if isinstance(v, str):
            return [c.strip() for c in v.split(',') if c.strip()]
        return v or []
    
    @validator('status')
    def validate_status(cls, v):
        """Validar que el estado sea válido"""
        if v is not None:
            valid_statuses = ['DRAFT', 'PUBLISHED', 'CANCELLED', 'COMPLETED']
            if v.upper() not in valid_statuses:
                raise ValueError(f"Estado debe ser uno de: {', '.join(valid_statuses)}")
            return v.upper()
        return v

class EventSearchResponse(BaseModel):
    """
    Respuesta paginada para búsqueda de eventos
    """
    events: List[Dict[str, Any]] = Field(..., description="Lista de eventos encontrados")
    total: int = Field(..., description="Total de eventos que cumplen con los criterios")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    total_pages: int = Field(..., description="Total de páginas disponibles")
    
    class Config:
        schema_extra = {
            "example": {
                "events": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Concierto de Rock",
                        "description": "El mejor concierto del año",
                        "startDate": "2025-12-01T20:00:00",
                        "endDate": "2025-12-01T23:00:00",
                        "venue": "Estadio Nacional",
                        "totalCapacity": 5000,
                        "status": "PUBLISHED",
                        "availableTickets": 2500,
                        "isSoldOut": False,
                        "minPrice": 50.0,
                        "maxPrice": 200.0,
                        "category": {
                            "id": "456e7890-e89b-12d3-a456-426614174001",
                            "name": "Conciertos",
                            "slug": "conciertos",
                            "icon": "🎵",
                            "color": "#FF5733"
                        }
                    }
                ],
                "total": 45,
                "page": 1,
                "page_size": 20,
                "total_pages": 3
            }
        }

class CategoryResponse(BaseModel):
    """
    Respuesta para categorías de eventos
    """
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

class OrganizerEventResponse(BaseModel):
    id: UUID
    title: str
    date: datetime
    location: str
    totalTickets: int
    soldTickets: int
    status: str
    imageUrl: Optional[str] = None

    # Permite que Pydantic lea los datos desde un modelo de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)

class EventCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    slug: str = Field(..., min_length=1, max_length=120)
    icon: Optional[str] = None
    color: Optional[str] = None
    image_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: int = 0
    level: int = 0
    is_active: bool = True
    is_featured: bool = False

class EventCategoryCreate(EventCategoryBase):
    pass

class EventCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=120)
    icon: Optional[str] = None
    color: Optional[str] = None
    image_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    parent_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    level: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None

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
# 🧾 Event Detail Schema (extendido con ticket_types)
# =========================================================
class EventDetailResponse(EventResponse):
    """
    Respuesta detallada de evento con tipos de tickets incluidos.
    """
    organizer: Optional[OrganizerInfo] = None
    category: Optional[CategoryInfo] = None

    # 👇 Nuevo campo
    ticket_types: List[TicketTypeResponse] = Field(default_factory=list)

    class Config:
        orm_mode = True
        from_attributes = True
        allow_population_by_field_name = True
