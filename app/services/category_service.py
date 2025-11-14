from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from uuid import UUID

from app.repositories.category_repository import EventCategoryRepository
from app.schemas.category import EventCategoryResponse, EventCategoryListResponse
from app.models.event_category import EventCategory


class EventCategoryService:
    """Service layer for event category business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = EventCategoryRepository(db)
    
    def get_all_categories(self, active_only: bool = True) -> EventCategoryListResponse:
        """Get all categories"""
        categories = self.category_repo.get_all_categories(active_only=active_only)
        
        category_responses = [
            self._category_to_response(category) for category in categories
        ]
        
        return EventCategoryListResponse(
            categories=category_responses,
            total=len(category_responses)
        )
    
    def get_featured_categories(self) -> List[EventCategoryResponse]:
        """Get featured categories"""
        categories = self.category_repo.get_featured_categories()
        
        return [self._category_to_response(category) for category in categories]
    
    def get_category(self, category_id: UUID) -> EventCategoryResponse:
        """Get category by ID"""
        category = self.category_repo.get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        
        return self._category_to_response(category)
    
    def get_category_by_slug(self, slug: str) -> EventCategoryResponse:
        """Get category by slug"""
        category = self.category_repo.get_category_by_slug(slug)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        
        return self._category_to_response(category)
    
    def _category_to_response(self, category: EventCategory) -> EventCategoryResponse:
        """Convert EventCategory model to EventCategoryResponse"""
        return EventCategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            slug=category.slug,
            icon=category.icon,
            color=category.color,
            imageUrl=category.image_url,
            metaTitle=category.meta_title,
            metaDescription=category.meta_description,
            parentId=category.parent_id,
            sortOrder=category.sort_order,
            level=category.level,
            isActive=category.is_active,
            isFeatured=category.is_featured,
            eventCount=category.event_count,
            createdAt=category.created_at,
            updatedAt=category.updated_at
        )
