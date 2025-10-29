from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum

class PromotionType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    BUY_ONE_GET_ONE = "BUY_ONE_GET_ONE"
    EARLY_BIRD = "EARLY_BIRD"

class PromotionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    USED_UP = "USED_UP"

class PromotionBase(BaseModel):
    name: str
    description: Optional[str] = None
    code: str = Field(..., min_length=3, max_length=50)
    promotion_type: PromotionType
    discount_value: float
    max_discount_amount: Optional[float] = None
    min_purchase_amount: Optional[float] = None
    max_uses: Optional[int] = None
    max_uses_per_user: Optional[int] = None
    start_date: datetime
    end_date: datetime
    applies_to_new_users_only: bool = False
    is_public: bool = True

class PromotionCreate(PromotionBase):
    event_id: UUID
    created_by_id: UUID

class PromotionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    discount_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[PromotionStatus] = None

class PromotionResponse(PromotionBase):
    id: UUID
    status: PromotionStatus
    event_ids: Optional[List[UUID]] = []
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
