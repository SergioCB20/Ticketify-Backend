from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.utils.security import CREDENTIALS_EXCEPTION

# Security scheme
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        print(f"[DEBUG] Token received: {token[:20]}...")  # Log para debug
        auth_service = AuthService(db)
        user = auth_service.get_current_user(token)
        print(f"[DEBUG] User authenticated: {user.email}")  # Log para debug
        return user
    except HTTPException as he:
        # Re-raise HTTP exceptions from auth_service
        print(f"[DEBUG] HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        print(f"[DEBUG] Generic Exception: {str(e)}")  # Log para debug
        raise CREDENTIALS_EXCEPTION

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.isActive:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    return current_user

def require_role(allowed_roles: list[UserRole]):
    """Decorator to require specific user roles"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        # Check if user has any of the required roles through the Role relationship
        user_role_names = [role.name for role in current_user.roles]
        
        # Convert UserRole enums to strings for comparison
        allowed_role_names = [role.value for role in allowed_roles]
        
        if not any(role_name in allowed_role_names for role_name in user_role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes"
            )
        return current_user
    return role_checker

# Common role dependencies usando los nuevos roles
get_organizer_user = require_role([UserRole.ORGANIZER])
get_attendee_user = require_role([UserRole.ATTENDEE])
get_organizer_or_attendee = require_role([UserRole.ORGANIZER, UserRole.ATTENDEE])

def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if token is provided, None otherwise"""
    if not credentials:
        return None
        
    try:
        token = credentials.credentials
        auth_service = AuthService(db)
        user = auth_service.get_current_user(token)
        return user if user.isActive else None
    except Exception:
        return None

# ============= DEPENDENCIAS PARA ADMINISTRADORES =============

def require_super_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Requiere que el usuario sea SUPER_ADMIN"""
    user_role_names = [role.name for role in current_user.roles]
    
    if 'SUPER_ADMIN' not in user_role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de Super Administrador"
        )
    return current_user

def require_any_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Requiere que el usuario tenga cualquier rol de administrador"""
    user_role_names = [role.name for role in current_user.roles]
    admin_roles = ['SUPER_ADMIN', 'SUPPORT_ADMIN', 'SECURITY_ADMIN', 'CONTENT_ADMIN']
    
    if not any(role in admin_roles for role in user_role_names):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de Administrador"
        )
    return current_user

def require_support_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Requiere que el usuario sea SUPER_ADMIN o SUPPORT_ADMIN"""
    user_role_names = [role.name for role in current_user.roles]
    
    if 'SUPER_ADMIN' not in user_role_names and 'SUPPORT_ADMIN' not in user_role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de Soporte"
        )
    return current_user

def require_security_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Requiere que el usuario sea SUPER_ADMIN o SECURITY_ADMIN"""
    user_role_names = [role.name for role in current_user.roles]
    
    if 'SUPER_ADMIN' not in user_role_names and 'SECURITY_ADMIN' not in user_role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de Seguridad"
        )
    return current_user

def require_content_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Requiere que el usuario sea SUPER_ADMIN o CONTENT_ADMIN"""
    user_role_names = [role.name for role in current_user.roles]
    
    if 'SUPER_ADMIN' not in user_role_names and 'CONTENT_ADMIN' not in user_role_names:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de Contenido"
        )
    return current_user
