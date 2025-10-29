from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import math

from app.models.user import User
from app.models.role import Role
from app.schemas.admin import (
    UserListResponse, UserDetailResponse, PaginatedUsersResponse,
    AdminListResponse, AdminStatsResponse
)

class AdminService:
    """Servicio para operaciones administrativas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============= USUARIOS =============
    
    def get_users_paginated(
        self,
        page: int = 1,
        page_size: int = 8,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PaginatedUsersResponse:
        """Obtener usuarios paginados (excluyendo admins)"""
        
        # Query base - solo usuarios sin roles de admin
        query = self.db.query(User).outerjoin(User.roles)
        
        # Filtrar usuarios que NO tienen roles de admin
        admin_role_names = ['SUPER_ADMIN', 'SUPPORT_ADMIN', 'SECURITY_ADMIN', 'CONTENT_ADMIN']
        query = query.filter(
            ~User.roles.any(Role.name.in_(admin_role_names))
        )
        
        # Aplicar filtros
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.firstName.ilike(f"%{search}%"),
                User.lastName.ilike(f"%{search}%"),
                User.documentId.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(User.isActive == is_active)
        
        # Contar total
        total = query.count()
        
        # Calcular paginación
        total_pages = math.ceil(total / page_size)
        offset = (page - 1) * page_size
        
        # Obtener usuarios
        users = query.order_by(User.createdAt.desc()).offset(offset).limit(page_size).all()
        
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
        user = self.db.query(User).filter(User.id == user_id).first()
        
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
            profilePhoto=user.profilePhoto,
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
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        user.isActive = is_active
        
        # Aquí podrías registrar en un log de auditoría
        # audit_log = AuditLog(
        #     user_id=admin_id,
        #     action="BAN_USER" if not is_active else "UNBAN_USER",
        #     target_user_id=user_id,
        #     reason=reason
        # )
        # self.db.add(audit_log)
        
        self.db.commit()
        self.db.refresh(user)
        
        return self.get_user_by_id(user_id)
    
    # ============= ADMINISTRADORES =============
    
    def get_all_admins(self) -> List[AdminListResponse]:
        """Obtener todos los administradores"""
        admin_role_names = ['SUPER_ADMIN', 'SUPPORT_ADMIN', 'SECURITY_ADMIN', 'CONTENT_ADMIN']
        
        admins = self.db.query(User).join(User.roles).filter(
            Role.name.in_(admin_role_names)
        ).all()
        
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
    
    def update_admin_role(
        self,
        admin_id: UUID,
        new_role: str,
        updated_by: UUID
    ) -> Optional[AdminListResponse]:
        """Cambiar el rol de un administrador"""
        admin = self.db.query(User).filter(User.id == admin_id).first()
        
        if not admin:
            return None
        
        # Obtener el nuevo rol
        role = self.db.query(Role).filter(Role.name == new_role).first()
        
        if not role:
            # Si el rol no existe, crearlo
            role = Role(name=new_role, description=f"Rol de {new_role}")
            self.db.add(role)
            self.db.commit()
        
        # Remover roles antiguos de admin y asignar el nuevo
        admin_role_names = ['SUPER_ADMIN', 'SUPPORT_ADMIN', 'SECURITY_ADMIN', 'CONTENT_ADMIN']
        admin.roles = [r for r in admin.roles if r.name not in admin_role_names]
        admin.roles.append(role)
        
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
        admin = self.db.query(User).filter(User.id == admin_id).first()
        
        if not admin:
            return None
        
        admin.isActive = False
        self.db.commit()
        self.db.refresh(admin)
        
        roles = [role.name for role in admin.roles]
        
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
    
    def activate_admin(
        self,
        admin_id: UUID,
        activated_by: UUID
    ) -> Optional[AdminListResponse]:
        """Reactivar cuenta de administrador"""
        admin = self.db.query(User).filter(User.id == admin_id).first()
        
        if not admin:
            return None
        
        admin.isActive = True
        self.db.commit()
        self.db.refresh(admin)
        
        roles = [role.name for role in admin.roles]
        
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
    
    # ============= UTILIDADES =============
    
    def is_admin(self, user: User) -> bool:
        """Verificar si un usuario tiene rol de admin"""
        admin_role_names = ['SUPER_ADMIN', 'SUPPORT_ADMIN', 'SECURITY_ADMIN', 'CONTENT_ADMIN']
        return any(role.name in admin_role_names for role in user.roles)
    
    # ============= ESTADÍSTICAS =============
    
    def get_statistics(self) -> AdminStatsResponse:
        """Obtener estadísticas generales del sistema"""
        
        # Usuarios totales (sin admins)
        admin_role_names = ['SUPER_ADMIN', 'SUPPORT_ADMIN', 'SECURITY_ADMIN', 'CONTENT_ADMIN']
        total_users = self.db.query(User).outerjoin(User.roles).filter(
            ~User.roles.any(Role.name.in_(admin_role_names))
        ).count()
        
        # Usuarios activos
        active_users = self.db.query(User).outerjoin(User.roles).filter(
            ~User.roles.any(Role.name.in_(admin_role_names)),
            User.isActive == True
        ).count()
        
        # Usuarios baneados
        banned_users = total_users - active_users
        
        # Administradores totales
        total_admins = self.db.query(User).join(User.roles).filter(
            Role.name.in_(admin_role_names)
        ).count()
        
        # Administradores activos
        active_admins = self.db.query(User).join(User.roles).filter(
            Role.name.in_(admin_role_names),
            User.isActive == True
        ).count()
        
        # Registros recientes (últimos 7 días)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_registrations = self.db.query(User).filter(
            User.createdAt >= seven_days_ago
        ).count()
        
        # Total de eventos y tickets (si existen las tablas)
        try:
            from app.models.event import Event
            from app.models.ticket import Ticket
            total_events = self.db.query(Event).count()
            total_tickets = self.db.query(Ticket).count()
        except:
            total_events = 0
            total_tickets = 0
        
        return AdminStatsResponse(
            totalUsers=total_users,
            activeUsers=active_users,
            bannedUsers=banned_users,
            totalAdmins=total_admins,
            activeAdmins=active_admins,
            totalEvents=total_events,
            totalTickets=total_tickets,
            recentRegistrations=recent_registrations
        )
