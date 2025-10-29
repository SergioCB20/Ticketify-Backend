from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# ============= REQUEST SCHEMAS =============

class BanUserRequest(BaseModel):
    isActive: bool = Field(..., description="True para desbanear, False para banear")
    reason: Optional[str] = Field(None, max_length=500, description="Razón del baneo")
    
    class Config:
        populate_by_name = True

class UpdateAdminRoleRequest(BaseModel):
    role: str = Field(..., description="Nuevo rol: SUPER_ADMIN, SUPPORT_ADMIN, SECURITY_ADMIN, CONTENT_ADMIN")
    
    class Config:
        populate_by_name = True

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
    
    class Config:
        from_attributes = True
        populate_by_name = True

class UserDetailResponse(UserListResponse):
    profilePhoto: Optional[str]
    roles: List[str] = []
    
    class Config:
        from_attributes = True
        populate_by_name = True

class PaginatedUsersResponse(BaseModel):
    users: List[UserListResponse]
    total: int
    page: int
    pageSize: int = Field(..., alias="pageSize")
    totalPages: int = Field(..., alias="totalPages")
    
    class Config:
        populate_by_name = True

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
    
    class Config:
        from_attributes = True
        populate_by_name = True

class AdminStatsResponse(BaseModel):
    totalUsers: int = Field(..., alias="totalUsers")
    activeUsers: int = Field(..., alias="activeUsers")
    bannedUsers: int = Field(..., alias="bannedUsers")
    totalAdmins: int = Field(..., alias="totalAdmins")
    activeAdmins: int = Field(..., alias="activeAdmins")
    totalEvents: int = Field(..., alias="totalEvents")
    totalTickets: int = Field(..., alias="totalTickets")
    recentRegistrations: int = Field(..., alias="recentRegistrations", description="Últimos 7 días")
    
    class Config:
        populate_by_name = True
