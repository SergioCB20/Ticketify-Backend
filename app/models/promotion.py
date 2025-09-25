from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class PromotionType(str, enum.Enum):
    PERCENTAGE = "PERCENTAGE"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    BUY_ONE_GET_ONE = "BUY_ONE_GET_ONE"
    EARLY_BIRD = "EARLY_BIRD"

class PromotionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    USED_UP = "USED_UP"

class Promotion(Base):
    __tablename__ = "promotions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Promotion details
    promotion_type = Column(Enum(PromotionType), nullable=False)
    discount_value = Column(Numeric(10, 2), nullable=False)  # Percentage or fixed amount
    max_discount_amount = Column(Numeric(10, 2), nullable=True)  # Max discount for percentage
    min_purchase_amount = Column(Numeric(10, 2), nullable=True)  # Minimum purchase to apply
    
    # Usage limits
    max_uses = Column(Integer, nullable=True)  # Null = unlimited
    max_uses_per_user = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0, nullable=False)
    
    # Date range
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Applicability
    applies_to_all_events = Column(Boolean, default=False, nullable=False)
    applies_to_new_users_only = Column(Boolean, default=False, nullable=False)
    
    # Status
    status = Column(Enum(PromotionStatus), default=PromotionStatus.ACTIVE, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)  # Public or private code
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Foreign keys
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    created_by = relationship("User", back_populates="created_promotions")
    purchases = relationship("Purchase", back_populates="promotion")
    # Many-to-many relationship with events will be added separately
    
    def __repr__(self):
        return f"<Promotion(code='{self.code}', type='{self.promotion_type}')>"
    
    @property
    def is_active(self):
        """Check if promotion is currently active"""
        from datetime import datetime
        now = datetime.utcnow()
        
        return (
            self.status == PromotionStatus.ACTIVE and
            self.start_date <= now <= self.end_date and
            (self.max_uses is None or self.current_uses < self.max_uses)
        )
    
    @property
    def remaining_uses(self):
        """Get remaining uses for this promotion"""
        if self.max_uses is None:
            return None
        return max(0, self.max_uses - self.current_uses)
    
    @property
    def usage_percentage(self):
        """Get usage percentage"""
        if self.max_uses is None or self.max_uses == 0:
            return 0
        return (self.current_uses / self.max_uses) * 100
    
    def calculate_discount(self, purchase_amount: float) -> float:
        """Calculate discount amount for a given purchase amount"""
        if not self.is_active:
            return 0.0
            
        if self.min_purchase_amount and purchase_amount < float(self.min_purchase_amount):
            return 0.0
        
        discount = 0.0
        
        if self.promotion_type == PromotionType.PERCENTAGE:
            discount = purchase_amount * (float(self.discount_value) / 100)
            if self.max_discount_amount:
                discount = min(discount, float(self.max_discount_amount))
        elif self.promotion_type == PromotionType.FIXED_AMOUNT:
            discount = min(float(self.discount_value), purchase_amount)
        
        return discount
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "promotionType": self.promotion_type.value,
            "discountValue": float(self.discount_value) if self.discount_value else None,
            "maxDiscountAmount": float(self.max_discount_amount) if self.max_discount_amount else None,
            "minPurchaseAmount": float(self.min_purchase_amount) if self.min_purchase_amount else None,
            "maxUses": self.max_uses,
            "maxUsesPerUser": self.max_uses_per_user,
            "currentUses": self.current_uses,
            "remainingUses": self.remaining_uses,
            "usagePercentage": self.usage_percentage,
            "startDate": self.start_date.isoformat() if self.start_date else None,
            "endDate": self.end_date.isoformat() if self.end_date else None,
            "appliesToAllEvents": self.applies_to_all_events,
            "appliesToNewUsersOnly": self.applies_to_new_users_only,
            "status": self.status.value,
            "isPublic": self.is_public,
            "isActive": self.is_active,
            "createdById": str(self.created_by_id),
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
