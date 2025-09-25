from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister, UserLogin, AuthResponse, UserResponse, 
    MessageResponse, RefreshToken, ChangePassword, 
    ForgotPassword, PasswordReset, UserUpdate
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
async def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user with email and password"""
    auth_service = AuthService(db)
    return auth_service.login_user(credentials)

@router.post("/refresh", response_model=dict)
async def refresh_access_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    auth_service = AuthService(db)
    access_token, refresh_token = auth_service.refresh_token(refresh_data.refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", response_model=MessageResponse)
async def logout_user(
    current_user: User = Depends(get_current_user)
):
    """Logout current user (client-side token invalidation)"""
    # In JWT stateless approach, logout is mainly client-side
    # Server could maintain a blacklist of tokens if needed
    return MessageResponse(
        message="Logged out successfully",
        success=True
    )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        avatar=current_user.avatar,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    from app.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    updated_user = user_repo.update_user(current_user.id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update profile"
        )
    
    return UserResponse(
        id=str(updated_user.id),
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        role=updated_user.role,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        avatar=updated_user.avatar,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        last_login=updated_user.last_login
    )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    auth_service = AuthService(db)
    success = auth_service.change_password(
        current_user.id, 
        password_data.current_password, 
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )
    
    return MessageResponse(
        message="Password changed successfully",
        success=True
    )

@router.post("/forgot-password", response_model=MessageResponse)
async def request_password_reset(
    reset_data: ForgotPassword,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    auth_service = AuthService(db)
    auth_service.request_password_reset(reset_data.email)
    
    # Always return success for security reasons
    return MessageResponse(
        message="If the email exists, you will receive password reset instructions",
        success=True
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    auth_service = AuthService(db)
    success = auth_service.reset_password(reset_data.token, reset_data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return MessageResponse(
        message="Password reset successfully",
        success=True
    )

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user email using verification token"""
    auth_service = AuthService(db)
    success = auth_service.verify_email(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return MessageResponse(
        message="Email verified successfully",
        success=True
    )

@router.delete("/account", response_model=MessageResponse)
async def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete current user account"""
    from app.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    success = user_repo.delete_user(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete account"
        )
    
    return MessageResponse(
        message="Account deleted successfully",
        success=True
    )
