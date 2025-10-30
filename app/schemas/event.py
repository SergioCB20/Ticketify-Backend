from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class EventSimpleResponse(BaseModel):
    id: UUID
    title: str
    startDate: datetime 
    venue: str
    multimedia: Optional[List[str]] = None

    class Config:
        from_attributes = True
        populate_by_name = True