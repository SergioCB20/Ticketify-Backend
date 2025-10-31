from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

# Define cómo se verá el JSON que enviamos al frontend
class OrganizerEventResponse(BaseModel):
    id: uuid.UUID
    title: str
    date: datetime
    location: str
    totalTickets: int
    soldTickets: int
    status: str
    imageUrl: Optional[str] = None

    # Permite que Pydantic lea los datos desde un modelo de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)