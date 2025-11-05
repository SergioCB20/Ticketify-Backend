# category_repository.py

from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import Optional, List, Tuple
from uuid import UUID

from app.models.event_category import EventCategory
from app.models.event import Event, EventStatus
from app.schemas.event import EventCategoryCreate, EventCategoryUpdate


class CategoryRepository:
    """Repository for EventCategory database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: UUID) -> Optional[EventCategory]:
        """Get a category by ID"""
        return (
            self.db.query(EventCategory)
            .filter(EventCategory.id == category_id)
            .first()
        )

    def get_by_slug(self, slug: str) -> Optional[EventCategory]:
        """Get a category by slug"""
        return (
            self.db.query(EventCategory)
            .filter(EventCategory.slug == slug)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        include_event_count: bool = True
    ) -> List[Tuple[EventCategory, int]]:
        """
        Get all categories with optional filters and event count.
        
        Returns:
            List of tuples (EventCategory, event_count)
        """
        if include_event_count:
            # Query with event count (only published events)
            query = (
                self.db.query(
                    EventCategory,
                    func.count(Event.id).label('event_count')
                )
                .outerjoin(
                    Event,
                    (Event.category_id == EventCategory.id) & 
                    (Event.status == EventStatus.PUBLISHED)
                )
                .group_by(EventCategory.id)
            )
        else:
            # Simple query without count
            query = self.db.query(EventCategory, func.literal(0).label('event_count'))

        # Apply filters
        if is_active is not None:
            query = query.filter(EventCategory.is_active == is_active)

        if is_featured is not None:
            query = query.filter(EventCategory.is_featured == is_featured)

        # Order, paginate and return
        results = (
            query
            .order_by(EventCategory.sort_order.asc(), EventCategory.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return results

    def get_featured_categories(self, limit: int = 10) -> List[Tuple[EventCategory, int]]:
        """Get featured categories with event count"""
        return (
            self.db.query(
                EventCategory,
                func.count(Event.id).label('event_count')
            )
            .outerjoin(
                Event,
                (Event.category_id == EventCategory.id) & 
                (Event.status == EventStatus.PUBLISHED)
            )
            .filter(
                EventCategory.is_active == True,
                EventCategory.is_featured == True
            )
            .group_by(EventCategory.id)
            .order_by(EventCategory.sort_order.asc())
            .limit(limit)
            .all()
        )

    def create(self, category_data: EventCategoryCreate) -> EventCategory:
        """Create a new category"""
        db_category = EventCategory(**category_data.dict())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update(
        self, 
        category_id: UUID, 
        category_data: EventCategoryUpdate
    ) -> Optional[EventCategory]:
        """Update a category"""
        category = self.get_by_id(category_id)
        
        if not category:
            return None

        # Update only provided fields
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(category, field):
                setattr(category, field, value)

        category.updated_at = func.now()
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: UUID) -> bool:
        """Delete a category"""
        category = self.get_by_id(category_id)
        
        if not category:
            return False

        self.db.delete(category)
        self.db.commit()
        return True

    def count_events_in_category(self, category_id: UUID) -> int:
        """Count events in a specific category"""
        return (
            self.db.query(func.count(Event.id))
            .filter(
                Event.category_id == category_id,
                Event.status == EventStatus.PUBLISHED
            )
            .scalar() or 0
        )

    def get_subcategories(self, parent_id: UUID) -> List[EventCategory]:
        """Get all subcategories of a parent category"""
        return (
            self.db.query(EventCategory)
            .filter(
                EventCategory.parent_id == parent_id,
                EventCategory.is_active == True
            )
            .order_by(EventCategory.sort_order.asc())
            .all()
        )
