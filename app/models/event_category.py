from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class EventCategory(Base):
    __tablename__ = "event_categories"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic information
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(120), unique=True, index=True, nullable=False)
    
    # Visual elements
    icon = Column(String(100), nullable=True)  # Icon name or emoji
    color = Column(String(7), nullable=True)  # Hex color code
    image_url = Column(String(500), nullable=True)
    
    # SEO and metadata
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # Hierarchy and ordering
    parent_id = Column(UUID(as_uuid=True), nullable=True)  # Self-referencing for subcategories
    sort_order = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=0, nullable=False)  # 0 = root, 1 = subcategory, etc.
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    events = relationship("Event", back_populates="category")
    user_preferences = relationship("UserCategoryPreference", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EventCategory(name='{self.name}', slug='{self.slug}')>"
    
    @property
    def event_count(self):
        """Get number of events in this category"""
        return len(self.events)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "slug": self.slug,
            "icon": self.icon,
            "color": self.color,
            "imageUrl": self.image_url,
            "metaTitle": self.meta_title,
            "metaDescription": self.meta_description,
            "parentId": str(self.parent_id) if self.parent_id else None,
            "sortOrder": self.sort_order,
            "level": self.level,
            "isActive": self.is_active,
            "isFeatured": self.is_featured,
            "eventCount": self.event_count,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None
        }
