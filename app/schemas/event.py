# app/schemas/event.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

# Este schema define la estructura de CADA evento que el frontend recibirá
class OrganizerEventResponse(BaseModel):
    id: uuid.UUID
    title: str
    date: datetime
    location: str
    totalTickets: int
    soldTickets: int
    status: str
    imageUrl: Optional[str] = None

    # Esto le dice a Pydantic que puede leer datos
    # directamente desde un modelo de SQLAlchemy (como la clase Event)
    model_config = ConfigDict(from_attributes=True)