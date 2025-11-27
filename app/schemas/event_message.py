"""
Schemas para EventMessage
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class EventMessageCreate(BaseModel):
    """Schema para crear un nuevo mensaje a asistentes"""
    subject: str = Field(..., min_length=1, max_length=200, description="Asunto del mensaje")
    content: str = Field(..., min_length=1, max_length=5000, description="Contenido HTML del mensaje")
    message_type: str = Field(default="BROADCAST", description="Tipo de mensaje: BROADCAST, FILTERED, INDIVIDUAL")
    recipient_filters: Optional[str] = Field(None, description="Filtros en formato JSON para seleccionar destinatarios")


class EventMessageUpdate(BaseModel):
    """Schema para actualizar estadísticas de un mensaje"""
    successful_sends: int = Field(..., ge=0)
    failed_sends: int = Field(..., ge=0)


class EventMessageResponse(BaseModel):
    """Schema de respuesta para un mensaje"""
    id: str
    subject: str
    content: str
    messageType: str
    totalRecipients: int
    successfulSends: int
    failedSends: int
    successRate: float
    recipientFilters: Optional[str]
    sentAt: Optional[str]
    isSent: bool
    eventId: str
    organizerId: str
    createdAt: str
    updatedAt: str

    class Config:
        from_attributes = True


class EventAttendeeResponse(BaseModel):
    """Schema para información de un asistente"""
    id: str
    email: str
    firstName: str
    lastName: str
    ticketCount: int
    ticketTypes: list[str]

    class Config:
        from_attributes = True


class MessageStatsResponse(BaseModel):
    """Schema para estadísticas de mensajes de un evento"""
    totalMessages: int
    totalRecipients: int
    averageSuccessRate: float
    lastMessageSent: Optional[str]
