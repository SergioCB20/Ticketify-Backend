"""
Schemas para la compra directa de tickets
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
from decimal import Decimal



class CreatePreferenceRequest(BaseModel):
    """
    Schema para la solicitud de creación de preferencia.
    """
    eventId: UUID
    ticketTypeId: UUID
    quantity: int
    # promoCode: str | None = None # (Opcional, si manejas promos)

    class Config:
        orm_mode = True

class CreatePreferenceResponse(BaseModel):
    """
    Respuesta con el init_point para el frontend.
    """
    purchaseId: UUID
    init_point: str

    class Config:
        orm_mode = True

        
class PurchaseTicketRequest(BaseModel):
    """Request para comprar tickets de un evento"""
    eventId: UUID = Field(..., description="ID del evento")
    ticketTypeId: UUID = Field(..., description="ID del tipo de ticket")
    quantity: int = Field(..., ge=1, le=10, description="Cantidad de tickets (máximo 10)")
    
    class Config:
        populate_by_name = True


class PaymentData(BaseModel):
    """Datos de pago simulados (ficticios)"""
    cardNumber: str = Field(..., min_length=13, max_length=19, description="Número de tarjeta")
    cardholderName: str = Field(..., min_length=3, max_length=100, description="Nombre del titular")
    expiryMonth: str = Field(..., pattern=r'^(0[1-9]|1[0-2])$', description="Mes de expiración (01-12)")
    expiryYear: str = Field(..., pattern=r'^\d{2}$', description="Año de expiración (YY)")
    cvv: str = Field(..., pattern=r'^\d{3,4}$', description="CVV")
    
    @validator('cardNumber')
    def validate_card_number(cls, v):
        """Validación básica del número de tarjeta (solo dígitos)"""
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 13 or len(digits_only) > 19:
            raise ValueError('Número de tarjeta inválido')
        return digits_only
    
    class Config:
        populate_by_name = True


class ProcessPaymentRequest(BaseModel):
    """Request completo para procesar el pago"""
    purchase: PurchaseTicketRequest
    payment: PaymentData
    
    class Config:
        populate_by_name = True


class TicketResponse(BaseModel):
    """Respuesta con información del ticket generado"""
    id: UUID
    eventId: UUID
    ticketTypeId: UUID
    price: float
    qrCode: str
    status: str
    purchaseDate: str
    
    class Config:
        from_attributes = True
        populate_by_name = True


class PurchaseResponse(BaseModel):
    """Respuesta tras completar una compra"""
    success: bool
    message: str
    purchaseId: UUID
    paymentId: UUID
    tickets: list[TicketResponse]
    totalAmount: float
    
    class Config:
        populate_by_name = True
