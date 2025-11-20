from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import math
from fastapi import HTTPException, status

# Importaciones de Modelos y Esquemas
from app.models.user import User, AdminRole
from app.models.role import Role
from app.models.event import Event
from app.models.ticket import Ticket
from app.schemas.admin import (
    UserListResponse, UserDetailResponse, PaginatedUsersResponse,
    AdminListResponse, AdminStats, CreateAdminRequest  # <-- Schemas actualizados
)

# Importaciones de Repositorios y Utilidades
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.utils.security import get_password_hash # Para crear admin

class AdminService:
    """Servicio para operaciones administrativas"""
    
    def __init__(self, db: Session):
        # El servicio ahora usa repositorios
        self.db = db # Mantenemos la sesión por si algún repo la necesita
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
    
    # ============= USUARIOS =============
    
    def get_users_paginated(
        self,
        page: int = 1,
        page_size: int = 8,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PaginatedUsersResponse:
        """Obtener usuarios paginados (excluyendo admins)"""
        
        # Delegamos la lógica de consulta al repositorio
        users, total = self.user_repo.get_non_admin_users_paginated(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active
        )
        
        total_pages = math.ceil(total / page_size)
        
        # Convertir a response
        user_responses = [
            UserListResponse(
                id=str(user.id),
                email=user.email,
                firstName=user.firstName,
                lastName=user.lastName,
                phoneNumber=user.phoneNumber,
                documentId=user.documentId,
                isActive=user.isActive,
                createdAt=user.createdAt,
                lastLogin=user.lastLogin
            )
            for user in users
        ]
        
        return PaginatedUsersResponse(
            users=user_responses,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    def get_user_by_id(self, user_id: UUID) -> Optional[UserDetailResponse]:
        """Obtener usuario por ID con detalles completos"""
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            return None
        
        roles = [role.name for role in user.roles] if user.roles else []
        
        return UserDetailResponse(
            id=str(user.id),
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            phoneNumber=user.phoneNumber,
            documentId=user.documentId,
            profilePhoto=user.get_profile_photo_base64(),  # 🔧 CORREGIDO: usar método de conversión
            isActive=user.isActive,
            roles=roles,
            createdAt=user.createdAt,
            lastLogin=user.lastLogin
        )
    
    def ban_user(
        self,
        user_id: UUID,
        is_active: bool,
        reason: Optional[str] = None,
        admin_id: UUID = None
    ) -> UserDetailResponse:
        """Banear o desbanear un usuario"""
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            return None
        
        # Actualizamos usando el repositorio
        updated_user = self.user_repo.update(user, {"isActive": is_active})
        
        # Aquí la lógica de AuditLog...
        
        return self.get_user_by_id(updated_user.id)
    
    # ============= ADMINISTRADORES =============
    
    def get_all_admins(self) -> List[AdminListResponse]:
        """Obtener todos los administradores"""
        
        admins = self.user_repo.get_all_admins()
        
        admin_responses = []
        for admin in admins:
            roles = [role.name for role in admin.roles] if admin.roles else []
            admin_responses.append(
                AdminListResponse(
                    id=str(admin.id),
                    email=admin.email,
                    firstName=admin.firstName,
                    lastName=admin.lastName,
                    phoneNumber=admin.phoneNumber,
                    isActive=admin.isActive,
                    roles=roles,
                    createdAt=admin.createdAt,
                    lastLogin=admin.lastLogin
                )
            )
        
        return admin_responses
    
    # --- MÉTODO NUEVO ---
    def create_admin(self, admin_data: CreateAdminRequest, creator_id: UUID) -> AdminListResponse:
        """Crear un nuevo usuario administrador"""
        
        # 1. Verificar si el email ya existe
        existing_user = self.user_repo.get_by_email(admin_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado"
            )
        
        # 2. Obtener el rol de admin
        admin_role = self.role_repo.get_by_name(admin_data.role)
        if not admin_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol '{admin_data.role}' no existe"
            )

        # 3. Hashear contraseña
        hashed_password = get_password_hash(admin_data.password)
        
        # 4. Crear el objeto User
        new_admin_user = User(
            email=admin_data.email,
            password=hashed_password,
            firstName=admin_data.firstName,
            lastName=admin_data.lastName,
            phoneNumber=admin_data.phoneNumber,
            isActive=True
        )
        
        # 5. Crear usuario y asignarle rol
        # (Idealmente, tu user_repo tendría un método create_with_roles)
        new_admin_user.roles.append(admin_role)
        self.db.add(new_admin_user)
        self.db.commit()
        self.db.refresh(new_admin_user)
        
        # 6. Formatear y devolver la respuesta
        return AdminListResponse(
            id=str(new_admin_user.id),
            email=new_admin_user.email,
            firstName=new_admin_user.firstName,
            lastName=new_admin_user.lastName,
            phoneNumber=new_admin_user.phoneNumber,
            isActive=new_admin_user.isActive,
            roles=[admin_role.name],
            createdAt=new_admin_user.createdAt,
            lastLogin=new_admin_user.lastLogin
        )
    # --- FIN MÉTODO NUEVO ---

    def update_admin_role(
        self,
        admin_id: UUID,
        new_role: str,
        updated_by: UUID
    ) -> Optional[AdminListResponse]:
        """Cambiar el rol de un administrador"""
        admin = self.user_repo.get_by_id(admin_id)
        
        if not admin:
            return None
        
        # Obtener el nuevo rol
        role = self.role_repo.get_by_name(new_role)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El rol '{new_role}' no existe"
            )
        
        # Remover roles antiguos de admin y asignar el nuevo
        admin_role_names = [r.value for r in AdminRole]
        
        # (Esta lógica es compleja, idealmente iría en el user_repo)
        current_roles = [r for r in admin.roles if r.name not in admin_role_names]
        current_roles.append(role)
        admin.roles = current_roles
        
        self.db.commit()
        self.db.refresh(admin)
        
        roles = [r.name for r in admin.roles]
        
        return AdminListResponse(
            id=str(admin.id),
            email=admin.email,
            firstName=admin.firstName,
            lastName=admin.lastName,
            phoneNumber=admin.phoneNumber,
            isActive=admin.isActive,
            roles=roles,
            createdAt=admin.createdAt,
            lastLogin=admin.lastLogin
        )
    
    def deactivate_admin(
        self,
        admin_id: UUID,
        deactivated_by: UUID
    ) -> Optional[AdminListResponse]:
        """Desactivar cuenta de administrador"""
        admin = self.user_repo.get_by_id(admin_id)
        
        if not admin:
            return None
        
        updated_admin = self.user_repo.update(admin, {"isActive": False})
        
        roles = [role.name for role in updated_admin.roles]
        
        return AdminListResponse(
            id=str(updated_admin.id),
            email=updated_admin.email,
            firstName=updated_admin.firstName,
            lastName=updated_admin.lastName,
            phoneNumber=updated_admin.phoneNumber,
            isActive=updated_admin.isActive,
            roles=roles,
            createdAt=updated_admin.createdAt,
            lastLogin=updated_admin.lastLogin
        )
    
    def activate_admin(
        self,
        admin_id: UUID,
        activated_by: UUID
    ) -> Optional[AdminListResponse]:
        """Reactivar cuenta de administrador"""
        admin = self.user_repo.get_by_id(admin_id)
        
        if not admin:
            return None
            
        updated_admin = self.user_repo.update(admin, {"isActive": True})
        
        roles = [role.name for role in updated_admin.roles]
        
        return AdminListResponse(
            id=str(updated_admin.id),
            email=updated_admin.email,
            firstName=updated_admin.firstName,
            lastName=updated_admin.lastName,
            phoneNumber=updated_admin.phoneNumber,
            isActive=updated_admin.isActive,
            roles=roles,
            createdAt=updated_admin.createdAt,
            lastLogin=updated_admin.lastLogin
        )
    
    # ============= UTILIDADES =============
    
    def is_admin(self, user: User) -> bool:
        """Verificar si un usuario tiene rol de admin"""
        admin_role_names = [r.value for r in AdminRole]
        return any(role.name in admin_role_names for role in user.roles)
    
    # ============= ESTADÍSTICAS =============
    
    def get_statistics(self) -> AdminStats: # <-- CORREGIDO (AdminStatsResponse -> AdminStats)
        """Obtener estadísticas generales del sistema"""
        
        # (Idealmente, estas consultas estarían en el repositorio)
        
        admin_role_names = [r.value for r in AdminRole]
        
        # Usuarios totales (sin admins)
        total_users = self.user_repo.count_non_admins()
        
        # Usuarios activos (sin admins)
        active_users = self.user_repo.count_non_admins(is_active=True)
        
        # Usuarios baneados
        banned_users = total_users - active_users
        
        # Administradores totales
        total_admins = self.user_repo.count_admins()
        
        # Administradores activos
        active_admins = self.user_repo.count_admins(is_active=True)
        
        # Registros recientes (últimos 7 días)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_registrations = self.user_repo.count_new_users_since(seven_days_ago)
        
        # Total de eventos y tickets
        try:
            total_events = self.db.query(func.count(Event.id)).scalar()
            total_tickets = self.db.query(func.count(Ticket.id)).scalar()
        except:
            total_events = 0
            total_tickets = 0
        
        return AdminStats(
            totalUsers=total_users,
            activeUsers=active_users,
            bannedUsers=banned_users,
            totalAdmins=total_admins,
            activeAdmins=active_admins,
            totalEvents=total_events,
            totalTickets=total_tickets,
            recentRegistrations=recent_registrations
        )
