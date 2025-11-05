# categories.py (API Layer / Presentation Layer)

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.dependencies import get_db
from app.services.category_service import CategoryService
from app.schemas.event import (
    EventCategoryResponse,
    EventCategoryCreate,
    EventCategoryUpdate
)

router = APIRouter(prefix="/categories", tags=["categories"])


# --- Dependency Injection ---

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    """Dependency to inject the category service"""
    return CategoryService(db)


# --- Endpoints ---

@router.get("/", response_model=List[EventCategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0, description="Número de categorías a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de categorías a retornar"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    is_featured: Optional[bool] = Query(None, description="Filtrar por categorías destacadas"),
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Obtener todas las categorías de eventos con el conteo de eventos publicados.
    
    - **skip**: Número de registros a omitir (para paginación)
    - **limit**: Número máximo de registros a retornar
    - **is_active**: Filtrar solo categorías activas (true) o inactivas (false)
    - **is_featured**: Filtrar solo categorías destacadas (true) o no destacadas (false)
    """
    return category_service.get_all_categories(
        skip=skip,
        limit=limit,
        is_active=is_active,
        is_featured=is_featured
    )


@router.get("/featured", response_model=List[EventCategoryResponse])
def get_featured_categories(
    limit: int = Query(10, ge=1, le=50, description="Número de categorías destacadas"),
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Obtener categorías destacadas con el conteo de eventos.
    Útil para mostrar en la página principal.
    """
    return category_service.get_featured_categories(limit=limit)


@router.get("/{category_id}", response_model=EventCategoryResponse)
def get_category(
    category_id: UUID,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Obtener una categoría específica por su ID.
    Incluye el conteo de eventos publicados en esa categoría.
    """
    return category_service.get_category_by_id(category_id)


@router.get("/slug/{slug}", response_model=EventCategoryResponse)
def get_category_by_slug(
    slug: str,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Obtener una categoría por su slug (URL-friendly name).
    Útil para rutas amigables como /categories/conciertos
    """
    return category_service.get_category_by_slug(slug)


@router.post("/", response_model=EventCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: EventCategoryCreate,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Crear una nueva categoría de eventos.
    Requiere permisos de administrador (agregar middleware de auth según necesidad).
    """
    return category_service.create_category(category_data)


@router.put("/{category_id}", response_model=EventCategoryResponse)
def update_category(
    category_id: UUID,
    category_data: EventCategoryUpdate,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Actualizar una categoría existente.
    Requiere permisos de administrador.
    """
    return category_service.update_category(category_id, category_data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Eliminar una categoría.
    No se puede eliminar si tiene eventos asociados.
    Requiere permisos de administrador.
    """
    category_service.delete_category(category_id)
    return None
