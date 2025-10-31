from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class EventCategoryResponse(BaseModel):
    """Schema for event category response"""
    id: UUID
    name: str
    description: Optional[str]
    slug: str
    icon: Optional[str]
    color: Optional[str]
    imageUrl: Optional[str]
    metaTitle: Optional[str]
    metaDescription: Optional[str]
    parentId: Optional[UUID]
    sortOrder: int
    level: int
    isActive: bool
    isFeatured: bool
    eventCount: int
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Conciertos",
                "description": "Eventos de música en vivo y conciertos de todos los géneros.",
                "slug": "conciertos",
                "icon": "fa-music",
                "color": "#E74C3C",
                "imageUrl": "https://tu-cdn.com/imagenes/conciertos.jpg",
                "metaTitle": "Entradas para Conciertos",
                "metaDescription": "Encuentra y compra entradas para los mejores conciertos en tu ciudad.",
                "parentId": None,
                "sortOrder": 0,
                "level": 0,
                "isActive": True,
                "isFeatured": True,
                "eventCount": 25,
                "createdAt": "2025-10-30T10:00:00",
                "updatedAt": "2025-10-30T10:00:00"
            }
        }


class EventCategoryListResponse(BaseModel):
    """Schema for list of categories"""
    categories: list[EventCategoryResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": [],
                "total": 6
            }
        }
