from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from .event import EventSimpleResponse  # Necesitarás crear este schema simple
from .user import UserSimpleResponse    # Necesitarás crear este schema simple

# --- SCHEMAS SIMPLIFICADOS ---
# (Puedes crear estos en app/schemas/event.py y app/schemas/user.py)
class EventSimpleResponse(BaseModel):
    id: UUID
    title: str
    startDate: datetime = Field(..., alias="startDate")
    venue: str
    multimedia: Optional[List[str]] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class UserSimpleResponse(BaseModel):
    id: UUID
    firstName: str = Field(..., alias="firstName")
    lastName: str = Field(..., alias="lastName")
    profilePhoto: Optional[str] = Field(None, alias="profilePhoto")

    class Config:
        from_attributes = True
        populate_by_name = True
# ---------------------------------


class MarketplaceListingResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    price: float
    originalPrice: Optional[float] = Field(None, alias="originalPrice")
    isNegotiable: bool = Field(..., alias="isNegotiable")
    status: str # Ya es un ENUM, str está bien
    sellerNotes: Optional[str] = Field(None, alias="sellerNotes")
    transferMethod: Optional[str] = Field(None, alias="transferMethod")
    createdAt: datetime = Field(..., alias="createdAt")
    expiresAt: Optional[datetime] = Field(None, alias="expiresAt")
    
    # Datos relacionados que el frontend necesita
    event: EventSimpleResponse
    seller: UserSimpleResponse
    
    ticketId: UUID = Field(..., alias="ticketId")
    eventId: UUID = Field(..., alias="eventId")
    sellerId: UUID = Field(..., alias="sellerId")

    class Config:
        from_attributes = True
        populate_by_name = True


class PaginatedMarketplaceListings(BaseModel):
    items: List[MarketplaceListingResponse]
    total: int
    page: int
    pageSize: int = Field(..., alias="pageSize")
    totalPages: int = Field(..., alias="totalPages")

    class Config:
        from_attributes = True
        populate_by_name = True