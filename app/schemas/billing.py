"""
Schemas para el sistema de facturación de organizadores
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============================================================
# Schemas de Comisiones
# ============================================================

class BillingCommissionSchema(BaseModel):
    """Comisión individual (MP o Plataforma)"""
    amount: Decimal = Field(..., description="Monto de la comisión")
    percentage: Decimal = Field(..., description="Porcentaje aplicado")
    
    model_config = ConfigDict(from_attributes=True)


class BillingCommissionsSchema(BaseModel):
    """Desglose completo de comisiones"""
    mercadoPago: BillingCommissionSchema = Field(..., description="Comisión de MercadoPago")
    platform: BillingCommissionSchema = Field(..., description="Comisión de la plataforma")
    total: Decimal = Field(..., description="Total de comisiones")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Schemas de Acreditación
# ============================================================

class BillingAccreditationSchema(BaseModel):
    """Información de acreditación de fondos"""
    credited: Decimal = Field(..., description="Monto ya acreditado")
    pending: Decimal = Field(..., description="Monto pendiente de acreditar")
    nextDate: Optional[datetime] = Field(None, description="Próxima fecha de acreditación")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Schemas de Resumen
# ============================================================

class BillingSummarySchema(BaseModel):
    """Resumen financiero del evento"""
    totalRevenue: Decimal = Field(..., description="Ingresos totales")
    totalTransactions: int = Field(..., description="Cantidad de transacciones")
    commissions: BillingCommissionsSchema = Field(..., description="Desglose de comisiones")
    netAmount: Decimal = Field(..., description="Monto neto para el organizador")
    accreditation: BillingAccreditationSchema = Field(..., description="Estado de acreditación")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Schemas de Métodos de Pago
# ============================================================

class PaymentMethodSchema(BaseModel):
    """Distribución por método de pago"""
    method: str = Field(..., description="Método de pago")
    count: int = Field(..., description="Cantidad de transacciones")
    amount: Decimal = Field(..., description="Monto total del método")
    percentage: Decimal = Field(..., description="Porcentaje del total")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Schemas de Transacciones
# ============================================================

class BillingTransactionSchema(BaseModel):
    """Transacción individual con detalles de facturación"""
    id: str = Field(..., description="ID de la transacción")
    mpPaymentId: Optional[str] = Field(None, description="ID del pago en MercadoPago")
    date: datetime = Field(..., description="Fecha de la transacción")
    buyerEmail: str = Field(..., description="Email del comprador")
    amount: Decimal = Field(..., description="Monto total")
    mpCommission: Decimal = Field(..., description="Comisión de MercadoPago")
    platformCommission: Decimal = Field(..., description="Comisión de la plataforma")
    netAmount: Decimal = Field(..., description="Monto neto")
    status: str = Field(..., description="Estado del pago")
    paymentMethod: str = Field(..., description="Método de pago")
    accreditationDate: Optional[datetime] = Field(None, description="Fecha de acreditación")
    mpLink: Optional[str] = Field(None, description="Link al pago en MercadoPago")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Schema de Detalle Completo del Evento
# ============================================================

class EventBillingDetailSchema(BaseModel):
    """Detalle completo de facturación de un evento"""
    eventId: str = Field(..., description="ID del evento")
    eventName: str = Field(..., description="Nombre del evento")
    eventDate: datetime = Field(..., description="Fecha del evento")
    summary: BillingSummarySchema = Field(..., description="Resumen financiero")
    paymentMethods: List[PaymentMethodSchema] = Field(..., description="Distribución de métodos de pago")
    transactions: List[BillingTransactionSchema] = Field(..., description="Lista de transacciones")
    lastSync: datetime = Field(..., description="Última sincronización con MercadoPago")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Schema de Lista de Eventos
# ============================================================

class OrganizerEventBillingSchema(BaseModel):
    """Resumen de facturación de un evento para lista"""
    id: str = Field(..., description="ID del evento")
    title: str = Field(..., description="Título del evento")
    startDate: datetime = Field(..., description="Fecha de inicio")
    totalRevenue: Decimal = Field(..., description="Ingresos totales")
    totalTransactions: int = Field(..., description="Cantidad de transacciones")
    netAmount: Decimal = Field(..., description="Monto neto")
    status: str = Field(..., description="Estado del evento")
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# Schema de Respuestas
# ============================================================

class BillingSyncResponseSchema(BaseModel):
    """Respuesta de sincronización con MercadoPago"""
    message: str = Field(..., description="Mensaje de resultado")
    transactionsUpdated: int = Field(..., description="Cantidad de transacciones actualizadas")
    lastSync: datetime = Field(..., description="Timestamp de la sincronización")
    
    model_config = ConfigDict(from_attributes=True)
