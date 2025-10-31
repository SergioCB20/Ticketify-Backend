from app.repositories.event_repository import EventRepository
from app.schemas.event import OrganizerEventResponse
from app.models.ticket import Ticket
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
import uuid

class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db=db)

    def get_organizer_events(self, organizer_id: uuid.UUID) -> list[OrganizerEventResponse]:
        # 1. Pide los eventos a la BD
        db_events = self.event_repo.get_events_by_organizer_id(organizer_id)
        
        response_events = []
        for event in db_events:
            # 2. Lógica de negocio (Calcular tickets vendidos)
            stmt = select(func.count(Ticket.id)).where(
                Ticket.event_id == event.id,
                Ticket.status.notin_(['CANCELLED'])
            )
            sold_tickets_count = self.db.execute(stmt).scalar_one()

            # 3. Lógica de negocio (Obtener imagen principal)
            main_image_url = event.multimedia[0] if event.multimedia else None

            # 4. "Traduce" los nombres de la BD a los nombres del Frontend
            response_event_data = {
                "id": event.id,
                "title": event.title,
                "date": event.startDate,  # BD (start_date) -> Frontend (date)
                "location": event.venue,   # BD (venue) -> Frontend (location)
                "totalTickets": event.totalCapacity,
                "soldTickets": sold_tickets_count,
                "status": str(event.status.value),
                "imageUrl": main_image_url
            }

            # 5. Valida y agrega a la lista final
            response_events.append(OrganizerEventResponse.model_validate(response_event_data))
        
        return response_events
