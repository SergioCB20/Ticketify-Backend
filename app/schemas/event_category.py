from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

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

class EventCategoryResponse(EventCategoryBase):
    id: UUID
    event_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
