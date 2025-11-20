from pydantic import BaseModel, ConfigDict, Field, condecimal
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from .event import EventSimpleResponse
from .user import UserSimpleResponse


# --- RENOMBRADA DE 'MarketplaceListingResponse' ---
class ListingResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    price: float
    originalPrice: Optional[float] = Field(None, alias="original_price")
    isNegotiable: bool = Field(..., alias="is_negotiable")
    isFeatured: bool = Field(..., alias="is_featured")
    status: str 
    sellerNotes: Optional[str] = Field(None, alias="seller_notes")
    transferMethod: Optional[str] = Field(None, alias="transfer_method")
    createdAt: datetime = Field(..., alias="created_at")
    expiresAt: Optional[datetime] = Field(None, alias="expires_at")
    soldAt: Optional[datetime] = Field(None, alias="sold_at")
    views_count: str 
    inquiries_count: str 
    event: EventSimpleResponse
    seller: UserSimpleResponse
    ticketId: UUID = Field(..., alias="ticket_id")
    eventId: UUID = Field(..., alias="event_id")
    sellerId: UUID = Field(..., alias="seller_id")
    buyerId: Optional[UUID] = Field(None, alias="buyer_id")
    ticketTypeId: UUID = Field(..., alias="ticket_type_id")
    
    # --- SINTAXIS ACTUALIZADA ---
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedMarketplaceListings(BaseModel):
    items: List[ListingResponse] # Ahora coincide
    total: int
    page: int
    pageSize: int = Field(..., alias="pageSize")
    totalPages: int = Field(..., alias="totalPages")

    # --- SINTAXIS ACTUALIZADA ---
    model_config = ConfigDict(populate_by_name=True)


# --- RENOMBRADA DE 'MarketplaceListingCreate' ---
class CreateListingRequest(BaseModel):
    ticketId: UUID = Field(..., alias="ticketId")
    price: condecimal(gt=0, decimal_places=2)
    description: Optional[str] = Field(None, max_length=500)
    
    # --- SINTAXIS ACTUALIZADA ---
    model_config = ConfigDict(populate_by_name=True)

class UpdateListingRequest(BaseModel):
    """Schema para actualizar un listing"""
    price: Optional[condecimal(gt=0, decimal_places=2)] = None
    description: Optional[str] = Field(None, max_length=500)
    is_cancelled: Optional[bool] = None

    # Sintaxis de Pydantic V2
    model_config = ConfigDict(populate_by_name=True)
    
class MarketplacePurchaseRequest(BaseModel):
    """Request para iniciar compra de marketplace (si se necesita data adicional)"""
    pass


class MarketplacePurchaseResponse(BaseModel):
    """Respuesta con la URL de pago de MercadoPago para marketplace"""
    listingId: UUID = Field(..., description="ID del listing")
    init_point: str = Field(..., description="URL de MercadoPago para completar el pago")
    preferenceId: str = Field(..., description="ID de la preferencia creada")

    # --- SINTAXIS ACTUALIZADA ---
    model_config = ConfigDict(populate_by_name=True)
      
      
class MarketplacePreferenceRequest(BaseModel):
    listing_id: UUID

# Schema para la respuesta al frontend
class MarketplacePreferenceResponse(BaseModel):
    listing_id: UUID
    init_point: str

    model_config = ConfigDict(from_attributes=True)