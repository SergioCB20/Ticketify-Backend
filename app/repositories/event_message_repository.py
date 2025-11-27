"""
Repository para EventMessage
Maneja las operaciones CRUD de mensajes a asistentes
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.event_message import EventMessage, MessageType
from app.schemas.event_message import EventMessageCreate, EventMessageUpdate


class EventMessageRepository:
    """Repository para operaciones de EventMessage"""

    def __init__(self, db: Session):
        self.db = db

    def create_message(
        self,
        event_id: UUID,
        organizer_id: UUID,
        message_data: EventMessageCreate
    ) -> EventMessage:
        """Crear un nuevo mensaje"""
        message = EventMessage(
            event_id=event_id,
            organizer_id=organizer_id,
            subject=message_data.subject,
            content=message_data.content,
            message_type=MessageType(message_data.message_type),
            recipient_filters=message_data.recipient_filters
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_message_by_id(self, message_id: UUID) -> Optional[EventMessage]:
        """Obtener un mensaje por ID"""
        return self.db.query(EventMessage).filter(
            EventMessage.id == message_id
        ).first()

    def get_messages_by_event(
        self,
        event_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[EventMessage]:
        """Obtener todos los mensajes de un evento (paginado)"""
        return self.db.query(EventMessage).filter(
            EventMessage.event_id == event_id
        ).order_by(desc(EventMessage.created_at)).offset(skip).limit(limit).all()

    def get_messages_by_organizer(
        self,
        organizer_id: UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[EventMessage]:
        """Obtener todos los mensajes enviados por un organizador"""
        return self.db.query(EventMessage).filter(
            EventMessage.organizer_id == organizer_id
        ).order_by(desc(EventMessage.created_at)).offset(skip).limit(limit).all()

    def update_message_stats(
        self,
        message_id: UUID,
        successful_sends: int,
        failed_sends: int
    ) -> Optional[EventMessage]:
        """Actualizar estadísticas de envío de un mensaje"""
        message = self.get_message_by_id(message_id)
        if message:
            message.update_stats(successful_sends, failed_sends)
            message.mark_as_sent()
            self.db.commit()
            self.db.refresh(message)
        return message

    def count_messages_by_event(self, event_id: UUID) -> int:
        """Contar mensajes de un evento"""
        return self.db.query(EventMessage).filter(
            EventMessage.event_id == event_id
        ).count()

    def get_message_stats(self, event_id: UUID) -> dict:
        """Obtener estadísticas de mensajes de un evento"""
        messages = self.db.query(EventMessage).filter(
            EventMessage.event_id == event_id
        ).all()

        if not messages:
            return {
                "totalMessages": 0,
                "totalRecipients": 0,
                "averageSuccessRate": 0.0,
                "lastMessageSent": None
            }

        total_recipients = sum(m.total_recipients for m in messages)
        success_rates = [m.success_rate for m in messages if m.total_recipients > 0]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0.0

        last_sent = max((m.sent_at for m in messages if m.sent_at), default=None)

        return {
            "totalMessages": len(messages),
            "totalRecipients": total_recipients,
            "averageSuccessRate": round(avg_success_rate, 2),
            "lastMessageSent": last_sent.isoformat() if last_sent else None
        }

    def delete_message(self, message_id: UUID) -> bool:
        """Eliminar un mensaje"""
        message = self.get_message_by_id(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False
