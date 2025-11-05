from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# ============= BASE SCHEMAS =============

class TicketTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    quantity_available: int = Field(..., gt=0, alias="quantity")
    min_purchase: int = Field(1, ge=1)
    max_purchase: int = Field(10, ge=1, alias="maxPerPurchase")
    sale_start_date: Optional[datetime] = Field(None, alias="salesStartDate")
    sale_end_date: Optional[datetime] = Field(None, alias="salesEndDate")

    @validator('max_purchase')
    def validate_max_purchase(cls, v, values):
        if 'min_purchase' in values and v < values['min_purchase']:
            raise ValueError('max_purchase must be greater than or equal to min_purchase')
        return v
    
    @validator('sale_end_date')
    def validate_sale_dates(cls, v, values):
        if v and 'sale_start_date' in values and values['sale_start_date']:
            if v < values['sale_start_date']:
                raise ValueError('sale_end_date must be after sale_start_date')
        return v

# ============= CREATE SCHEMAS =============

class TicketTypeCreate(TicketTypeBase):
    """Schema para crear un tipo de entrada"""
    pass

class TicketTypeBatchCreate(BaseModel):
    """Schema para crear múltiples tipos de entrada a la vez"""
    eventId: UUID
    ticketTypes: List[TicketTypeCreate]

# ============= UPDATE SCHEMAS =============

class TicketTypeUpdate(BaseModel):
    """Schema para actualizar un tipo de entrada (todos los campos opcionales)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    quantity_available: Optional[int] = Field(None, gt=0)
    min_purchase: Optional[int] = Field(None, ge=1)
    max_purchase: Optional[int] = Field(None, ge=1)
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

# ============= RESPONSE SCHEMAS =============

class TicketTypeResponse(BaseModel):
    id: UUID
    eventId: UUID
    name: str
    description: Optional[str] = None
    price: float
    originalPrice: Optional[float] = None
    quantityAvailable: int
    soldQuantity: int
    remainingQuantity: int
    minPurchase: int
    maxPurchase: int
    saleStartDate: Optional[datetime] = None
    saleEndDate: Optional[datetime] = None
    isActive: bool
    isFeatured: bool
    isSoldOut: bool
    isOnSale: bool
    sortOrder: int
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class TicketTypeSimple(BaseModel):
    """Schema simplificado para incluir en respuestas de eventos"""
    id: UUID
    name: str
    price: float
    quantityAvailable: int
    remainingQuantity: int
    isOnSale: bool
    
    class Config:
        from_attributes = True
