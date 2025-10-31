from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Request schemas
class EventCreate(BaseModel):
    """Schema for creating a new event"""
    title: str = Field(..., min_length=3, max_length=200, description="Event title")
    description: Optional[str] = Field(None, description="Event description")
    startDate: datetime = Field(..., description="Event start date and time")
    endDate: datetime = Field(..., description="Event end date and time")
    venue: str = Field(..., min_length=3, max_length=200, description="Event venue/location")
    totalCapacity: int = Field(..., gt=0, description="Total capacity of the event")
    multimedia: Optional[List[str]] = Field(default=[], description="List of image/video URLs")
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
                "multimedia": ["https://example.com/image1.jpg"],
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
    multimedia: Optional[List[str]] = None
    category_id: Optional[UUID] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Concierto Rock en Vivo 2025 - ACTUALIZADO",
                "totalCapacity": 6000
            }
        }

# Response schemas
class EventResponse(BaseModel):
    """Schema for event response"""
    id: UUID
    title: str
    description: Optional[str]
    startDate: datetime
    endDate: datetime
    venue: str
    totalCapacity: int
    status: str
    multimedia: List[str]
    availableTickets: int
    isSoldOut: bool
    organizerId: UUID
    categoryId: Optional[UUID]
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Concierto Rock en Vivo 2025",
                "description": "Las mejores bandas de rock en un solo lugar",
                "startDate": "2025-11-15T20:00:00",
                "endDate": "2025-11-15T23:00:00",
                "venue": "Estadio Nacional, Lima",
                "totalCapacity": 5000,
                "status": "PUBLISHED",
                "multimedia": ["https://example.com/image1.jpg"],
                "availableTickets": 4850,
                "isSoldOut": False,
                "organizerId": "123e4567-e89b-12d3-a456-426614174001",
                "categoryId": "123e4567-e89b-12d3-a456-426614174002",
                "createdAt": "2025-10-30T10:00:00",
                "updatedAt": "2025-10-30T10:00:00"
            }
        }

class EventListResponse(BaseModel):
    """Schema for list of events"""
    events: List[EventResponse]
    total: int
    page: int
    pageSize: int
    totalPages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "events": [],
                "total": 100,
                "page": 1,
                "pageSize": 10,
                "totalPages": 10
            }
        }

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operación exitosa",
                "success": True
            }
        }

class EventStatusUpdate(BaseModel):
    """Schema for updating event status"""
    status: str = Field(..., pattern="^(DRAFT|PUBLISHED|CANCELLED|COMPLETED)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "PUBLISHED"
            }
        }
