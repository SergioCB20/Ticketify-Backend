# category_service.py

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.repositories.category_repository import CategoryRepository
from app.schemas.event import (
    EventCategoryCreate,
    EventCategoryUpdate,
    EventCategoryResponse
)
from app.models.event_category import EventCategory


class CategoryService:
    """Category service with business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)

    def get_all_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        is_featured: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all categories with event count.
        Returns list of dictionaries ready for API response.
        """
        # Get categories with event count from repository
        results = self.category_repo.get_all(
            skip=skip,
            limit=limit,
            is_active=is_active,
            is_featured=is_featured,
            include_event_count=True
        )

        # Transform to response format
        categories = []
        for category, event_count in results:
            category_dict = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "slug": category.slug,
                "icon": category.icon,
                "color": category.color,
                "imageUrl": category.image_url,
                "metaTitle": category.meta_title,
                "metaDescription": category.meta_description,
                "parentId": category.parent_id,
                "sortOrder": category.sort_order,
                "level": category.level,
                "isActive": category.is_active,
                "isFeatured": category.is_featured,
                "eventCount": event_count,  # Event count from repository
                "createdAt": category.created_at,
                "updatedAt": category.updated_at
            }
            categories.append(category_dict)

        return categories

    def get_category_by_id(self, category_id: UUID) -> EventCategoryResponse:
        """Get a single category by ID"""
        category = self.category_repo.get_by_id(category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        # Get event count for this category
        event_count = self.category_repo.count_events_in_category(category_id)

        # Build response
        category_dict = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "slug": category.slug,
            "icon": category.icon,
            "color": category.color,
            "imageUrl": category.image_url,
            "metaTitle": category.meta_title,
            "metaDescription": category.meta_description,
            "parentId": category.parent_id,
            "sortOrder": category.sort_order,
            "level": category.level,
            "isActive": category.is_active,
            "isFeatured": category.is_featured,
            "eventCount": event_count,
            "createdAt": category.created_at,
            "updatedAt": category.updated_at
        }

        return EventCategoryResponse(**category_dict)

    def get_category_by_slug(self, slug: str) -> EventCategoryResponse:
        """Get a single category by slug"""
        category = self.category_repo.get_by_slug(slug)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        # Get event count for this category
        event_count = self.category_repo.count_events_in_category(category.id)

        # Build response
        category_dict = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "slug": category.slug,
            "icon": category.icon,
            "color": category.color,
            "imageUrl": category.image_url,
            "metaTitle": category.meta_title,
            "metaDescription": category.meta_description,
            "parentId": category.parent_id,
            "sortOrder": category.sort_order,
            "level": category.level,
            "isActive": category.is_active,
            "isFeatured": category.is_featured,
            "eventCount": event_count,
            "createdAt": category.created_at,
            "updatedAt": category.updated_at
        }

        return EventCategoryResponse(**category_dict)

    def get_featured_categories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get featured categories with event count"""
        results = self.category_repo.get_featured_categories(limit=limit)

        categories = []
        for category, event_count in results:
            category_dict = {
                "id": category.id,
                "name": category.name,
                "description": category.description,
                "slug": category.slug,
                "icon": category.icon,
                "color": category.color,
                "imageUrl": category.image_url,
                "metaTitle": category.meta_title,
                "metaDescription": category.meta_description,
                "parentId": category.parent_id,
                "sortOrder": category.sort_order,
                "level": category.level,
                "isActive": category.is_active,
                "isFeatured": category.is_featured,
                "eventCount": event_count,
                "createdAt": category.created_at,
                "updatedAt": category.updated_at
            }
            categories.append(category_dict)

        return categories

    def create_category(self, category_data: EventCategoryCreate) -> EventCategoryResponse:
        """Create a new category"""
        # Validate unique slug
        existing = self.category_repo.get_by_slug(category_data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Una categoría con el slug '{category_data.slug}' ya existe"
            )

        # Create category
        category = self.category_repo.create(category_data)

        # Return response
        category_dict = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "slug": category.slug,
            "icon": category.icon,
            "color": category.color,
            "imageUrl": category.image_url,
            "metaTitle": category.meta_title,
            "metaDescription": category.meta_description,
            "parentId": category.parent_id,
            "sortOrder": category.sort_order,
            "level": category.level,
            "isActive": category.is_active,
            "isFeatured": category.is_featured,
            "eventCount": 0,  # New category has no events
            "createdAt": category.created_at,
            "updatedAt": category.updated_at
        }

        return EventCategoryResponse(**category_dict)

    def update_category(
        self,
        category_id: UUID,
        category_data: EventCategoryUpdate
    ) -> EventCategoryResponse:
        """Update a category"""
        # Check if category exists
        existing = self.category_repo.get_by_id(category_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        # Validate unique slug if updating
        if category_data.slug and category_data.slug != existing.slug:
            slug_exists = self.category_repo.get_by_slug(category_data.slug)
            if slug_exists:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Una categoría con el slug '{category_data.slug}' ya existe"
                )

        # Update category
        updated_category = self.category_repo.update(category_id, category_data)

        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar la categoría"
            )

        # Get event count
        event_count = self.category_repo.count_events_in_category(category_id)

        # Return response
        category_dict = {
            "id": updated_category.id,
            "name": updated_category.name,
            "description": updated_category.description,
            "slug": updated_category.slug,
            "icon": updated_category.icon,
            "color": updated_category.color,
            "imageUrl": updated_category.image_url,
            "metaTitle": updated_category.meta_title,
            "metaDescription": updated_category.meta_description,
            "parentId": updated_category.parent_id,
            "sortOrder": updated_category.sort_order,
            "level": updated_category.level,
            "isActive": updated_category.is_active,
            "isFeatured": updated_category.is_featured,
            "eventCount": event_count,
            "createdAt": updated_category.created_at,
            "updatedAt": updated_category.updated_at
        }

        return EventCategoryResponse(**category_dict)

    def delete_category(self, category_id: UUID) -> Dict[str, str]:
        """Delete a category"""
        # Check if category exists
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )

        # Check if category has events
        event_count = self.category_repo.count_events_in_category(category_id)
        if event_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar la categoría porque tiene {event_count} evento(s) asociado(s)"
            )

        # Delete category
        success = self.category_repo.delete(category_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la categoría"
            )

        return {"message": "Categoría eliminada exitosamente"}
