"""
Servicio para envío de mensajes a asistentes de eventos
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime

from app.models.event import Event
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.event_message import EventMessage
from app.repositories.event_message_repository import EventMessageRepository
from app.schemas.event_message import EventMessageCreate, EventAttendeeResponse
from app.utils.email_service import email_service


class EventMessageService:
    """Servicio para gestión de mensajes a asistentes"""

    def __init__(self, db: Session):
        self.db = db
        self.message_repo = EventMessageRepository(db)

    def get_event_attendees(
        self,
        event_id: UUID,
        ticket_type_id: Optional[UUID] = None
    ) -> List[Dict]:
        """
        Obtener todos los asistentes únicos de un evento
        
        Args:
            event_id: ID del evento
            ticket_type_id: Filtrar por tipo de ticket (opcional)
            
        Returns:
            Lista de asistentes con información de sus tickets
        """
        query = self.db.query(
            User.id,
            User.email,
            User.firstName,
            User.lastName,
            func.count(Ticket.id).label('ticket_count')
        ).join(
            Ticket, Ticket.user_id == User.id
        ).filter(
            Ticket.event_id == event_id,
            Ticket.status == TicketStatus.ACTIVE,
            User.isActive == True
        )

        # Aplicar filtro de tipo de ticket si se especifica
        if ticket_type_id:
            query = query.filter(Ticket.ticket_type_id == ticket_type_id)

        query = query.group_by(User.id, User.email, User.firstName, User.lastName)
        
        attendees = query.all()

        # Obtener los tipos de ticket de cada asistente
        result = []
        for attendee in attendees:
            ticket_types = self.db.query(
                TicketType.name
            ).join(
                Ticket, Ticket.ticket_type_id == TicketType.id
            ).filter(
                Ticket.user_id == attendee.id,
                Ticket.event_id == event_id,
                Ticket.status == TicketStatus.ACTIVE
            ).distinct().all()

            result.append({
                "id": str(attendee.id),
                "email": attendee.email,
                "firstName": attendee.firstName,
                "lastName": attendee.lastName,
                "ticketCount": attendee.ticket_count,
                "ticketTypes": [tt.name for tt in ticket_types]
            })

        return result

    def send_message_to_attendees(
        self,
        event_id: UUID,
        organizer_id: UUID,
        message_data: EventMessageCreate
    ) -> EventMessage:
        """
        Enviar mensaje a los asistentes de un evento
        
        Args:
            event_id: ID del evento
            organizer_id: ID del organizador
            message_data: Datos del mensaje
            
        Returns:
            EventMessage creado con estadísticas
        """
        # Validar que el evento existe y pertenece al organizador
        event = self.db.query(Event).filter(
            Event.id == event_id,
            Event.organizer_id == organizer_id
        ).first()

        if not event:
            raise ValueError("Evento no encontrado o no pertenece al organizador")

        # Obtener el organizador
        organizer = self.db.query(User).filter(User.id == organizer_id).first()
        if not organizer:
            raise ValueError("Organizador no encontrado")

        # Crear el registro del mensaje
        message = self.message_repo.create_message(
            event_id=event_id,
            organizer_id=organizer_id,
            message_data=message_data
        )

        # Obtener asistentes
        attendees = self.get_event_attendees(event_id)

        if not attendees:
            # No hay asistentes, marcar como enviado con 0 destinatarios
            self.message_repo.update_message_stats(message.id, 0, 0)
            return message

        # Enviar emails
        successful = 0
        failed = 0

        for attendee in attendees:
            try:
                # Formatear fecha del evento
                event_date = event.startDate.strftime("%d/%m/%Y %H:%M")
                
                # Enviar email
                sent = email_service.send_organizer_message_email(
                    to_email=attendee["email"],
                    recipient_name=f"{attendee['firstName']} {attendee['lastName']}",
                    organizer_name=organizer.full_name,
                    event_title=event.title,
                    event_date=event_date,
                    event_venue=event.venue,
                    subject=message_data.subject,
                    message_content=message_data.content
                )

                if sent:
                    successful += 1
                else:
                    failed += 1

            except Exception as e:
                print(f"❌ Error enviando email a {attendee['email']}: {str(e)}")
                failed += 1

        # Actualizar estadísticas del mensaje
        self.message_repo.update_message_stats(message.id, successful, failed)

        return message

    def get_event_messages(
        self,
        event_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Dict:
        """
        Obtener mensajes de un evento (paginado)
        
        Args:
            event_id: ID del evento
            page: Número de página
            limit: Mensajes por página
            
        Returns:
            Dict con mensajes y metadata de paginación
        """
        skip = (page - 1) * limit
        messages = self.message_repo.get_messages_by_event(event_id, skip, limit)
        total = self.message_repo.count_messages_by_event(event_id)

        return {
            "messages": [m.to_dict() for m in messages],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }

    def get_message_by_id(
        self,
        event_id: UUID,
        message_id: UUID
    ) -> Optional[EventMessage]:
        """
        Obtener un mensaje específico
        
        Args:
            event_id: ID del evento
            message_id: ID del mensaje
            
        Returns:
            EventMessage o None si no existe
        """
        message = self.message_repo.get_message_by_id(message_id)
        
        if message and message.event_id == event_id:
            return message
        
        return None

    def get_message_stats(self, event_id: UUID) -> Dict:
        """
        Obtener estadísticas de mensajes de un evento
        
        Args:
            event_id: ID del evento
            
        Returns:
            Dict con estadísticas
        """
        return self.message_repo.get_message_stats(event_id)

    def validate_organizer_access(
        self,
        event_id: UUID,
        organizer_id: UUID
    ) -> bool:
        """
        Validar que el usuario es el organizador del evento
        
        Args:
            event_id: ID del evento
            organizer_id: ID del organizador
            
        Returns:
            True si es el organizador, False en caso contrario
        """
        event = self.db.query(Event).filter(
            Event.id == event_id,
            Event.organizer_id == organizer_id
        ).first()

        return event is not None
