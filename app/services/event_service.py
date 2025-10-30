# app/services/event_service.py

from app.repositories.event_repository import EventRepository
from app.schemas.event import OrganizerEventResponse
from app.models.ticket import Ticket # Importamos Ticket para el conteo
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
import uuid

class EventService:
    def __init__(self, db: Session):
        self.db = db
        self.event_repo = EventRepository(db=db)

    async def get_organizer_events(self, organizer_id: uuid.UUID) -> list[OrganizerEventResponse]:
        # 1. Obtiene los eventos de la BD
        db_events = await self.event_repo.get_events_by_organizer_id(organizer_id)
        
        response_events = []
        for event in db_events:
            # --- Aquí ocurre la "traducción" ---

            # 2. Lógica para calcular tickets vendidos (EJEMPLO)
            # Esto cuenta cuántos tickets para este evento NO están 'CANCELLED' o 'REFUNDED'
            # ¡Necesitarás ajustar esta lógica según tus reglas de negocio!
            stmt = select(func.count(Ticket.id)).where(
                Ticket.event_id == event.id,
                Ticket.status.notin_(['CANCELLED', 'REFUNDED'])
            )
            sold_tickets_count = (await self.db.execute(stmt)).scalar_one()

            # 3. Lógica para seleccionar la imagen principal
            # Toma la primera imagen de la lista 'multimedia', si existe
            main_image_url = event.multimedia[0] if event.multimedia else None #

            # 4. Construye el objeto de respuesta que el frontend espera
            response_event_data = {
                "id": event.id,
                "title": event.title,
                "date": event.start_date, # Frontend lo llama 'date', BD lo llama 'start_date'
                "location": event.venue,   # Frontend lo llama 'location', BD lo llama 'venue'
                "totalTickets": event.total_capacity, # Frontend 'totalTickets', BD 'total_capacity'
                "soldTickets": sold_tickets_count,
                "status": str(event.status.value), # Convierte el Enum de la BD a string
                "imageUrl": main_image_url
            }
            
            # Valida los datos con el schema y los añade a la lista
            response_events.append(OrganizerEventResponse.model_validate(response_event_data))
            
        return response_events