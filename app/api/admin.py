from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_super_admin, require_content_admin
from app.models.user import User
from app.schemas.admin import (
    UserListResponse, UserDetailResponse, BanUserRequest,
    AdminListResponse, UpdateAdminRoleRequest, PaginatedUsersResponse,
    CreateAdminRequest, AdminStats,
    CategoryResponse, CreateCategoryRequest, UpdateCategoryRequest
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin Management"])

# ============= USUARIOS NORMALES =============

@router.get("/users", response_model=PaginatedUsersResponse)
async def get_all_users(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(8, ge=1, le=50, description="Usuarios por página"),
    search: Optional[str] = Query(None, description="Buscar por nombre o email"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener lista paginada de usuarios normales (no admins)
    
    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    return admin_service.get_users_paginated(
        page=page,
        page_size=page_size,
        search=search,
        is_active=is_active
    )

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: UUID,
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener detalles de un usuario específico
    
    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    user = admin_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return user

@router.patch("/users/{user_id}/ban", response_model=UserDetailResponse)
async def ban_user(
    user_id: UUID,
    ban_data: BanUserRequest,
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Banear o desbanear un usuario (cambiar isActive)
    
    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    
    # No permitir banear a otros admins
    user = admin_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    if admin_service.is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes banear a un administrador desde esta sección"
        )
    
    updated_user = admin_service.ban_user(
        user_id=user_id,
        is_active=ban_data.isActive,
        reason=ban_data.reason,
        admin_id=current_admin.id
    )
    
    return updated_user

# ============= ADMINISTRADORES =============

@router.get("/admins", response_model=List[AdminListResponse])
async def get_all_admins(
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de todos los administradores
    
    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    return admin_service.get_all_admins()

# --- NUEVO ENDPOINT ---
@router.post("/admins", response_model=AdminListResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: CreateAdminRequest,
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo usuario Administrador
    
    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    # El servicio (admin_service.create_admin) debe manejar
    # la lógica de verificar si el email ya existe
    # y lanzar un HTTPException si es necesario.
    new_admin = admin_service.create_admin(
        admin_data=admin_data,
        creator_id=current_admin.id
    )
    return new_admin
# --- FIN NUEVO ENDPOINT ---

@router.patch("/admins/{admin_id}/role", response_model=AdminListResponse)
async def update_admin_role(
    admin_id: UUID,
    role_data: UpdateAdminRoleRequest,
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Cambiar el rol de un administrador
    
    Requiere: SUPER_ADMIN
    No puedes cambiar tu propio rol
    """
    if admin_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes cambiar tu propio rol"
        )
    
    admin_service = AdminService(db)
    updated_admin = admin_service.update_admin_role(
        admin_id=admin_id,
        new_role=role_data.role,
        updated_by=current_admin.id
    )
    
    if not updated_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrador no encontrado"
        )
    
    return updated_admin

@router.patch("/admins/{admin_id}/deactivate", response_model=AdminListResponse)
async def deactivate_admin(
    admin_id: UUID,
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Desactivar cuenta de un administrador
    
    Requiere: SUPER_ADMIN
    No puedes desactivarte a ti mismo
    """
    if admin_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes desactivar tu propia cuenta"
        )
    
    admin_service = AdminService(db)
    deactivated_admin = admin_service.deactivate_admin(
        admin_id=admin_id,
        deactivated_by=current_admin.id
    )
    
    if not deactivated_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrador no encontrado"
        )
    
    return deactivated_admin

@router.patch("/admins/{admin_id}/activate", response_model=AdminListResponse)
async def activate_admin(
    admin_id: UUID,
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Reactivar cuenta de un administrador
    
    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    activated_admin = admin_service.activate_admin(
        admin_id=admin_id,
        activated_by=current_admin.id
    )
    
    if not activated_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Administrador no encontrado"
        )
    
    return activated_admin

# ============= ESTADÍSTICAS =============

# --- CORREGIDO ---
# (Se añadió el response_model que espera el frontend)
@router.get("/stats", response_model=AdminStats) 
async def get_admin_stats(
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
# --- FIN CORRECCIÓN ---
    """
    Obtener estadísticas generales del sistema

    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    return admin_service.get_statistics()


# ============= CATEGORÍAS =============

@router.get("/categories", response_model=List[CategoryResponse])
async def get_all_categories(
    current_admin: User = Depends(require_content_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las categorías (incluidas inactivas)

    Requiere: SUPER_ADMIN o CONTENT_ADMIN
    """
    from app.models.event_category import EventCategory

    categories = db.query(EventCategory).order_by(EventCategory.sort_order, EventCategory.name).all()

    return [
        CategoryResponse(
            id=str(cat.id),
            name=cat.name,
            description=cat.description,
            slug=cat.slug,
            icon=cat.icon,
            color=cat.color,
            imageUrl=cat.image_url,
            isFeatured=cat.is_featured,
            isActive=cat.is_active,
            sortOrder=cat.sort_order,
            eventCount=len(cat.events) if cat.events else 0,
            createdAt=cat.created_at,
            updatedAt=cat.updated_at
        )
        for cat in categories
    ]


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CreateCategoryRequest,
    current_admin: User = Depends(require_content_admin),
    db: Session = Depends(get_db)
):
    """
    Crear una nueva categoría

    Requiere: SUPER_ADMIN o CONTENT_ADMIN
    """
    from app.models.event_category import EventCategory

    # Verificar si ya existe una categoría con ese nombre o slug
    existing_name = db.query(EventCategory).filter(EventCategory.name == category_data.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una categoría con el nombre '{category_data.name}'"
        )

    existing_slug = db.query(EventCategory).filter(EventCategory.slug == category_data.slug).first()
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una categoría con el slug '{category_data.slug}'"
        )

    # Crear nueva categoría
    new_category = EventCategory(
        name=category_data.name,
        description=category_data.description,
        slug=category_data.slug,
        icon=category_data.icon,
        color=category_data.color,
        image_url=category_data.imageUrl,
        is_featured=category_data.isFeatured,
        sort_order=category_data.sortOrder,
        is_active=True
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return CategoryResponse(
        id=str(new_category.id),
        name=new_category.name,
        description=new_category.description,
        slug=new_category.slug,
        icon=new_category.icon,
        color=new_category.color,
        imageUrl=new_category.image_url,
        isFeatured=new_category.is_featured,
        isActive=new_category.is_active,
        sortOrder=new_category.sort_order,
        eventCount=0,
        createdAt=new_category.created_at,
        updatedAt=new_category.updated_at
    )


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_data: UpdateCategoryRequest,
    current_admin: User = Depends(require_content_admin),
    db: Session = Depends(get_db)
):
    """
    Actualizar una categoría existente

    Requiere: SUPER_ADMIN o CONTENT_ADMIN
    """
    from app.models.event_category import EventCategory

    category = db.query(EventCategory).filter(EventCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    # Verificar unicidad de nombre (si se está cambiando)
    if category_data.name and category_data.name != category.name:
        existing_name = db.query(EventCategory).filter(
            EventCategory.name == category_data.name,
            EventCategory.id != category_id
        ).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoría con el nombre '{category_data.name}'"
            )

    # Verificar unicidad de slug (si se está cambiando)
    if category_data.slug and category_data.slug != category.slug:
        existing_slug = db.query(EventCategory).filter(
            EventCategory.slug == category_data.slug,
            EventCategory.id != category_id
        ).first()
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoría con el slug '{category_data.slug}'"
            )

    # Actualizar campos
    if category_data.name is not None:
        category.name = category_data.name
    if category_data.description is not None:
        category.description = category_data.description
    if category_data.slug is not None:
        category.slug = category_data.slug
    if category_data.icon is not None:
        category.icon = category_data.icon
    if category_data.color is not None:
        category.color = category_data.color
    if category_data.imageUrl is not None:
        category.image_url = category_data.imageUrl
    if category_data.isFeatured is not None:
        category.is_featured = category_data.isFeatured
    if category_data.sortOrder is not None:
        category.sort_order = category_data.sortOrder

    db.commit()
    db.refresh(category)

    return CategoryResponse(
        id=str(category.id),
        name=category.name,
        description=category.description,
        slug=category.slug,
        icon=category.icon,
        color=category.color,
        imageUrl=category.image_url,
        isFeatured=category.is_featured,
        isActive=category.is_active,
        sortOrder=category.sort_order,
        eventCount=len(category.events) if category.events else 0,
        createdAt=category.created_at,
        updatedAt=category.updated_at
    )


@router.delete("/categories/{category_id}", response_model=CategoryResponse)
async def delete_category(
    category_id: UUID,
    current_admin: User = Depends(require_content_admin),
    db: Session = Depends(get_db)
):
    """
    Desactivar una categoría (eliminación lógica)

    Requiere: SUPER_ADMIN o CONTENT_ADMIN
    """
    from app.models.event_category import EventCategory

    category = db.query(EventCategory).filter(EventCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    # Eliminación lógica
    category.is_active = False

    db.commit()
    db.refresh(category)

    return CategoryResponse(
        id=str(category.id),
        name=category.name,
        description=category.description,
        slug=category.slug,
        icon=category.icon,
        color=category.color,
        imageUrl=category.image_url,
        isFeatured=category.is_featured,
        isActive=category.is_active,
        sortOrder=category.sort_order,
        eventCount=len(category.events) if category.events else 0,
        createdAt=category.created_at,
        updatedAt=category.updated_at
    )


@router.patch("/categories/{category_id}/activate", response_model=CategoryResponse)
async def activate_category(
    category_id: UUID,
    current_admin: User = Depends(require_content_admin),
    db: Session = Depends(get_db)
):
    """
    Reactivar una categoría

    Requiere: SUPER_ADMIN o CONTENT_ADMIN
    """
    from app.models.event_category import EventCategory

    category = db.query(EventCategory).filter(EventCategory.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada"
        )

    category.is_active = True

    db.commit()
    db.refresh(category)

    return CategoryResponse(
        id=str(category.id),
        name=category.name,
        description=category.description,
        slug=category.slug,
        icon=category.icon,
        color=category.color,
        imageUrl=category.image_url,
        isFeatured=category.is_featured,
        isActive=category.is_active,
        sortOrder=category.sort_order,
        eventCount=len(category.events) if category.events else 0,
        createdAt=category.created_at,
        updatedAt=category.updated_at
    )