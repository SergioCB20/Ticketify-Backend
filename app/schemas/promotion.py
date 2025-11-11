from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum


# =========================================================
# ENUMS
# =========================================================
class PromotionType(str, Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"


class PromotionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    USED_UP = "USED_UP"


# =========================================================
# BASE SCHEMA
# =========================================================
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
    applies_to_all_events: bool = False
    applies_to_new_users_only: bool = False
    is_public: bool = True


# =========================================================
# CREATE / UPDATE
# =========================================================
class PromotionCreate(PromotionBase):
    event_id: UUID
    created_by_id: UUID


class PromotionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    promotion_type: Optional[PromotionType] = None
    discount_value: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True



# =========================================================
# RESPONSE
# =========================================================
class PromotionResponse(PromotionBase):
    id: UUID
    status: PromotionStatus
    event_id: UUID
    applies_to_all_events: bool
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True