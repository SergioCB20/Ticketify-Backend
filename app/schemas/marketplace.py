from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from .event import EventSimpleResponse
from .user import UserSimpleResponse
from pydantic import BaseModel, Field, condecimal
class MarketplaceListingResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    price: float
    

    originalPrice: Optional[float] = Field(None, alias="original_price")
    
    isNegotiable: bool = Field(..., alias="is_negotiable")
    isFeatured: bool = Field(..., alias="is_featured") # <-- Añadido por si acaso
    
    status: str 
    
    
    sellerNotes: Optional[str] = Field(None, alias="seller_notes")
    transferMethod: Optional[str] = Field(None, alias="transfer_method")
    createdAt: datetime = Field(..., alias="created_at")
    expiresAt: Optional[datetime] = Field(None, alias="expires_at")
    soldAt: Optional[datetime] = Field(None, alias="sold_at") # <-- Añadido por si acaso
    views_count: str 
    inquiries_count: str 
    
     
    event: EventSimpleResponse
    seller: UserSimpleResponse
    
    
    ticketId: UUID = Field(..., alias="ticket_id")
    eventId: UUID = Field(..., alias="event_id")
    sellerId: UUID = Field(..., alias="seller_id")
    buyerId: Optional[UUID] = Field(None, alias="buyer_id") # <-- Añadido por si acaso
    ticketTypeId: UUID = Field(..., alias="ticket_type_id")
    
 
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
        # Esta se queda SIN 'from_attributes = True'
        populate_by_name = True

class MarketplaceListingCreate(BaseModel):
    ticketId: UUID = Field(..., alias="ticketId")
    price: condecimal(gt=0, decimal_places=2)
    description: Optional[str] = Field(None, max_length=500)
    
    class Config:
        populate_by_name = True