from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# ============= BASE SCHEMAS =============

class TicketTypeBase(BaseModel):
    """Schema base para tipos de entrada"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del tipo de entrada")
    description: Optional[str] = Field(None, description="Descripción del tipo de entrada")
    price: float = Field(..., ge=0, description="Precio del ticket")
    quantity: int = Field(..., gt=0, description="Cantidad disponible", alias="quantity")
    min_purchase: int = Field(1, ge=1, description="Mínimo por compra")
    max_purchase: int = Field(10, ge=1, description="Máximo por compra", alias="maxPerPurchase")
    sale_start_date: Optional[datetime] = Field(None, description="Fecha inicio de ventas", alias="salesStartDate")
    sale_end_date: Optional[datetime] = Field(None, description="Fecha fin de ventas", alias="salesEndDate")

    @validator('max_purchase')
    def validate_max_purchase(cls, v, values):
        if 'min_purchase' in values and v < values['min_purchase']:
            raise ValueError('max_purchase debe ser mayor o igual a min_purchase')
        return v
    
    @validator('sale_end_date')
    def validate_sale_dates(cls, v, values):
        if v and 'sale_start_date' in values and values['sale_start_date']:
            if v < values['sale_start_date']:
                raise ValueError('sale_end_date debe ser posterior a sale_start_date')
        return v
    
    class Config:
        populate_by_name = True


# ============= CREATE SCHEMAS =============

class TicketTypeCreate(TicketTypeBase):
    """Schema para crear un tipo de entrada"""
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "General",
                "description": "Entrada general",
                "price": 50.00,
                "quantity": 100,
                "maxPerPurchase": 10,
                "salesStartDate": "2025-10-01T00:00:00",
                "salesEndDate": "2025-11-15T23:59:59"
            }
        }

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
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "General Actualizado",
                "price": 60.00,
                "quantity_available": 150
            }
        }

class TicketTypeUpdateItem(BaseModel):
    """Item usado en el batch de edición de tipos de entrada"""
    id: Optional[UUID] = None  # None => crear nuevo
    name: str
    description: Optional[str] = None
    price: float
    quantity: int = Field(..., gt=0, alias="quantity")
    maxPerPurchase: Optional[int] = Field(None, ge=1)

    class Config:
        populate_by_name = True

class TicketTypeBatchUpdate(BaseModel):
    eventId: UUID
    ticketTypes: List[TicketTypeUpdateItem] # puede traer id=None para crear

class TicketTypeBatchCreate(BaseModel):
    """Schema para crear múltiples tipos de entrada a la vez"""
    eventId: UUID = Field(..., description="ID del evento")
    ticketTypes: List[TicketTypeCreate] = Field(..., description="Lista de tipos de entrada")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "eventId": "123e4567-e89b-12d3-a456-426614174000",
                "ticketTypes": [
                    {
                        "name": "General",
                        "price": 50.00,
                        "quantity": 100,
                        "maxPerPurchase": 10
                    },
                    {
                        "name": "VIP",
                        "price": 150.00,
                        "quantity": 50,
                        "maxPerPurchase": 5
                    }
                ]
            }
        }

# ============= RESPONSE SCHEMAS =============

class TicketTypeResponse(BaseModel):
    """Schema de respuesta para tipo de entrada"""
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
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "eventId": "123e4567-e89b-12d3-a456-426614174001",
                "name": "General",
                "description": "Entrada general",
                "price": 50.00,
                "originalPrice": None,
                "quantityAvailable": 100,
                "soldQuantity": 0,
                "remainingQuantity": 100,
                "minPurchase": 1,
                "maxPurchase": 10,
                "saleStartDate": "2025-10-01T00:00:00",
                "saleEndDate": "2025-11-15T23:59:59",
                "isActive": True,
                "isFeatured": False,
                "isSoldOut": False,
                "isOnSale": True,
                "sortOrder": 0,
                "createdAt": "2025-10-30T10:00:00",
                "updatedAt": "2025-10-30T10:00:00"
            }
        }


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
        populate_by_name = True
