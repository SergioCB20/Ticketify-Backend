from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class UserSimpleResponse(BaseModel):
    id: UUID
    firstName: str 
    lastName: str 
    profilePhoto: Optional[str] = None
    class Config:
        from_attributes = True
        populate_by_name = True