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

    async def get_organizer_events(self, organizer_id: uuid.UUID) -> list[OrganizerEventResponse]:
        # 1. Pide los eventos a la BD
        db_events = await self.event_repo.get_events_by_organizer_id(organizer_id)
        
        response_events = []
        for event in db_events:
            # 2. Lógica de negocio (Calcular tickets vendidos)
            # (Ajusta esta lógica si es necesario)
            stmt = select(func.count(Ticket.id)).where(
                Ticket.event_id == event.id,
                Ticket.status.notin_(['CANCELLED', 'REFUNDED'])
            )
            sold_tickets_count = (await self.db.execute(stmt)).scalar_one()

            # 3. Lógica de negocio (Obtener imagen principal)
            main_image_url = event.multimedia[0] if event.multimedia else None

            # 4. "Traduce" los nombres de la BD a los nombres del Frontend
            response_event_data = {
                "id": event.id,
                "title": event.title,
                "date": event.start_date, # BD (start_date) -> Frontend (date)
                "location": event.venue,   # BD (venue) -> Frontend (location)
                "totalTickets": event.total_capacity, # BD (total_capacity) -> Frontend (totalTickets)
                "soldTickets": sold_tickets_count, # Dato calculado
                "status": str(event.status.value),
                "imageUrl": main_image_url # Dato procesado
            }
            
            # 5. Valida y agrega a la lista final
            response_events.append(OrganizerEventResponse.model_validate(response_event_data))
            
        return response_events