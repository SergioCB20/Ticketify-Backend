from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class UserSimpleResponse(BaseModel):
    id: UUID
    firstName: str = Field(..., alias="firstName")
    lastName: str = Field(..., alias="lastName")
    profilePhoto: Optional[str] = Field(None, alias="profilePhoto")

    class Config:
        from_attributes = True
        populate_by_name = True