from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class TicketTypeSelection(BaseModel):
    """Selección de tipos de tickets para compra"""
    ticketTypeId: UUID = Field(..., description="ID del tipo de ticket")
    quantity: int = Field(..., ge=1, description="Cantidad a comprar")

class CreatePreferenceRequest(BaseModel):
    """Request para crear preferencia de pago"""
    eventId: UUID = Field(..., description="ID del evento")
    tickets: List[TicketTypeSelection] = Field(..., description="Tickets a comprar")
    promotionCode: Optional[str] = Field(None, description="Código promocional (opcional)")
    
    @validator('tickets')
    def tickets_not_empty(cls, v):
        if not v:
            raise ValueError('Debe seleccionar al menos un ticket')
        return v

class CreatePreferenceResponse(BaseModel):
    """Response con el init_point de MercadoPago"""
    purchaseId: UUID
    initPoint: str = Field(..., alias="init_point")
    preferenceId: str
    
    class Config:
        populate_by_name = True

class PurchaseDetailResponse(BaseModel):
    """Detalle de una compra"""
    id: UUID
    totalAmount: Decimal
    subtotal: Decimal
    taxAmount: Decimal
    serviceFee: Decimal
    discountAmount: Decimal
    quantity: int
    status: str
    paymentMethod: Optional[str]
    paymentReference: Optional[str]
    buyerEmail: str
    purchaseDate: datetime
    paymentDate: Optional[datetime]
    eventId: UUID
    eventTitle: str
    tickets: List[dict]
    
    class Config:
        from_attributes = True
