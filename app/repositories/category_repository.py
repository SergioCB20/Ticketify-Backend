from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.models.event_category import EventCategory


class EventCategoryRepository:
    """Repository for EventCategory database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_categories(self, active_only: bool = True) -> List[EventCategory]:
        """Get all categories"""
        query = self.db.query(EventCategory)
        
        if active_only:
            query = query.filter(EventCategory.is_active == True)
        
        return query.order_by(EventCategory.sort_order.asc()).all()
    
    def get_featured_categories(self) -> List[EventCategory]:
        """Get featured categories"""
        return self.db.query(EventCategory).filter(
            EventCategory.is_active == True,
            EventCategory.is_featured == True
        ).order_by(EventCategory.sort_order.asc()).all()
    
    def get_category_by_id(self, category_id: UUID) -> Optional[EventCategory]:
        """Get category by ID"""
        return self.db.query(EventCategory).filter(
            EventCategory.id == category_id
        ).first()
    
    def get_category_by_slug(self, slug: str) -> Optional[EventCategory]:
        """Get category by slug"""
        return self.db.query(EventCategory).filter(
            EventCategory.slug == slug
        ).first()
    
    def get_root_categories(self) -> List[EventCategory]:
        """Get root level categories (level 0)"""
        return self.db.query(EventCategory).filter(
            EventCategory.is_active == True,
            EventCategory.level == 0
        ).order_by(EventCategory.sort_order.asc()).all()
