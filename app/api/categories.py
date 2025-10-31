from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.event_category import EventCategory
from app.schemas.event_category import EventCategoryResponse, EventCategoryCreate, EventCategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[EventCategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    is_featured: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las categorías de eventos
    """
    query = db.query(EventCategory)
    
    if is_active is not None:
        query = query.filter(EventCategory.is_active == is_active)
    
    if is_featured is not None:
        query = query.filter(EventCategory.is_featured == is_featured)
    
    categories = query.order_by(EventCategory.sort_order).offset(skip).limit(limit).all()
    
    return [EventCategoryResponse(**cat.to_dict()) for cat in categories]


@router.get("/{category_id}", response_model=EventCategoryResponse)
def get_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener una categoría por ID
    """
    category = db.query(EventCategory).filter(EventCategory.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return EventCategoryResponse(**category.to_dict())


@router.get("/slug/{slug}", response_model=EventCategoryResponse)
def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Obtener una categoría por slug
    """
    category = db.query(EventCategory).filter(EventCategory.slug == slug).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return EventCategoryResponse(**category.to_dict())
