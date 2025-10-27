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
        auth_service = AuthService(db)
        user = auth_service.get_current_user(token)
        return user
    except Exception:
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
