from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_super_admin
from app.models.user import User
from app.schemas.admin import (
    UserListResponse, UserDetailResponse, BanUserRequest,
    AdminListResponse, UpdateAdminRoleRequest, PaginatedUsersResponse
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

@router.get("/stats")
async def get_admin_stats(
    current_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas generales del sistema
    
    Requiere: SUPER_ADMIN
    """
    admin_service = AdminService(db)
    return admin_service.get_statistics()
