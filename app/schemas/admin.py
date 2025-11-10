from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Importamos el Enum de roles para validación
from app.models.user import AdminRole


# ============= REQUEST SCHEMAS =============

class BanUserRequest(BaseModel):
    isActive: bool = Field(..., description="True para desbanear, False para banear")
    reason: Optional[str] = Field(None, max_length=500, description="Razón del baneo")
    
    # Sintaxis actualizada para Pydantic v2
    model_config = ConfigDict(
        populate_by_name = True
    )

class UpdateAdminRoleRequest(BaseModel):
    # Usamos el Enum para validar que el rol sea uno de los permitidos
    role: AdminRole = Field(..., description="Nuevo rol de admin")
    
    model_config = ConfigDict(
        populate_by_name = True
    )

# --- NUEVO SCHEMA AÑADIDO ---
# (Requerido por AdminService.ts y admin/users.py router)
class CreateAdminRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña del nuevo admin")
    firstName: str = Field(..., min_length=2, max_length=100)
    lastName: str = Field(..., min_length=2, max_length=100)
    phoneNumber: Optional[str] = Field(None, description="Teléfono (opcional)")
    role: AdminRole = Field(..., description="Rol inicial del administrador")

    model_config = ConfigDict(
        populate_by_name = True
    )
# --- FIN NUEVO SCHEMA ---


# ============= RESPONSE SCHEMAS =============

class UserListResponse(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    phoneNumber: Optional[str]
    documentId: Optional[str]
    isActive: bool
    createdAt: datetime
    lastLogin: Optional[datetime]
    
    model_config = ConfigDict(
        from_attributes = True,
        populate_by_name = True
    )

class UserDetailResponse(UserListResponse):
    profilePhoto: Optional[str]
    roles: List[str] = []
    
    model_config = ConfigDict(
        from_attributes = True,
        populate_by_name = True
    )

class PaginatedUsersResponse(BaseModel):
    users: List[UserListResponse]
    total: int
    page: int
    pageSize: int = Field(..., alias="pageSize")
    totalPages: int = Field(..., alias="totalPages")
    
    model_config = ConfigDict(
        populate_by_name = True
    )

class AdminListResponse(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    phoneNumber: Optional[str]
    isActive: bool
    roles: List[str]
    createdAt: datetime
    lastLogin: Optional[datetime]
    
    model_config = ConfigDict(
        from_attributes = True,
        populate_by_name = True
    )

# --- NOMBRE CORREGIDO ---
# (AdminStatsResponse -> AdminStats)
class AdminStats(BaseModel):
# --- FIN CORRECCIÓN ---
    totalUsers: int = Field(..., alias="totalUsers")
    activeUsers: int = Field(..., alias="activeUsers")
    bannedUsers: int = Field(..., alias="bannedUsers")
    totalAdmins: int = Field(..., alias="totalAdmins")
    activeAdmins: int = Field(..., alias="activeAdmins")
    totalEvents: int = Field(..., alias="totalEvents")
    totalTickets: int = Field(..., alias="totalTickets")
    recentRegistrations: int = Field(..., alias="recentRegistrations", description="Últimos 7 días")
    
    model_config = ConfigDict(
        populate_by_name = True
    )