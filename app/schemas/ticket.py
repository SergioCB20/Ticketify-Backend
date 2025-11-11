from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from .event import EventSimpleResponse # (Ya lo creamos)

class TicketTypeSimpleResponse(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
        populate_by_name = True

class MyTicketResponse(BaseModel):
    id: UUID
    price: float
    purchaseDate: datetime = Field(..., alias="purchase_date")
    status: str
    isValid: bool = Field(..., alias="is_valid")
    
    event: EventSimpleResponse
    ticketType: TicketTypeSimpleResponse = Field(..., alias="ticket_type")
    
    # Para saber si ya está a la venta
    isListed: bool = Field(False, alias="is_listed")
    listingId: Optional[UUID] = Field(None, alias="listing_id")

    class Config:
        from_attributes = True
        populate_by_name = True