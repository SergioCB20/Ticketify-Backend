from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    startDate: datetime
    endDate: datetime
    venue: str = Field(..., min_length=1, max_length=200)
    totalCapacity: int = Field(..., gt=0)
    multimedia: Optional[List[str]] = []
    category_id: Optional[UUID] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    venue: Optional[str] = Field(None, min_length=1, max_length=200)
    totalCapacity: Optional[int] = Field(None, gt=0)
    multimedia: Optional[List[str]] = None
    category_id: Optional[UUID] = None

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
