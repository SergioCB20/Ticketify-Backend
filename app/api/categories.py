from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.services.category_service import EventCategoryService
from app.schemas.category import EventCategoryResponse, EventCategoryListResponse

router = APIRouter(prefix="/categories", tags=["Event Categories"])


@router.get("/", response_model=EventCategoryListResponse)
async def get_categories(
    active_only: bool = Query(True, description="Only return active categories"),
    db: Session = Depends(get_db)
):
    """
    Get all event categories
    
    Returns a list of all available event categories sorted by sort_order.
    By default, only returns active categories.
    """
    category_service = EventCategoryService(db)
    return category_service.get_all_categories(active_only=active_only)


@router.get("/featured", response_model=List[EventCategoryResponse])
async def get_featured_categories(
    db: Session = Depends(get_db)
):
    """
    Get featured categories
    
    Returns only categories marked as featured (is_featured = true).
    Useful for displaying main categories on homepage.
    """
    category_service = EventCategoryService(db)
    return category_service.get_featured_categories()


@router.get("/{category_id}", response_model=EventCategoryResponse)
async def get_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get category by ID
    
    Returns detailed information about a specific category.
    """
    category_service = EventCategoryService(db)
    return category_service.get_category(category_id)


@router.get("/slug/{slug}", response_model=EventCategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get category by slug
    
    Returns category information using its slug (e.g., 'conciertos', 'deportes').
    Useful for SEO-friendly URLs.
    """
    category_service = EventCategoryService(db)
    return category_service.get_category_by_slug(slug)
