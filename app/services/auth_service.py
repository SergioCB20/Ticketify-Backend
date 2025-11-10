from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegister, UserLogin, AuthResponse, UserResponse
from app.models.user import User
from app.utils.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    generate_reset_token,
    INVALID_CREDENTIALS_EXCEPTION,
    INACTIVE_USER_EXCEPTION
)


class AuthService:
    """Authentication service with business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def _get_user_roles(self, user: User) -> list[str]:
        """Get list of role names for a user"""
        return [role.name for role in user.roles] if user.roles else []
    
    def register_user(self, user_data: UserRegister) -> AuthResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado"
            )
        
        # Check if document ID already exists
        existing_doc = self.user_repo.get_by_document_id(user_data.documentId)
        if existing_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de documento ya está registrado"
            )
        
        # Create new user
        try:
            user = self.user_repo.create_user(user_data)
            
            # Generate tokens
            access_token = create_access_token(
                data={"sub": user.email, "user_id": str(user.id)}
            )
            refresh_token = create_refresh_token(
                data={"sub": user.email, "user_id": str(user.id)}
            )
            
            # Convert user to response format with roles
            user_response = UserResponse(
                id=str(user.id),
                email=user.email,
                firstName=user.firstName,
                lastName=user.lastName,
                phoneNumber=user.phoneNumber,
                documentType=user.documentType.value if user.documentType else None,
                documentId=user.documentId,
                country=user.country,
                city=user.city,
                gender=user.gender.value if user.gender else None,
                profilePhoto=user.get_profile_photo_base64(),
                isActive=user.isActive,
                roles=self._get_user_roles(user),
                createdAt=user.createdAt,
                lastLogin=user.lastLogin,
            mercadopago=user.get_mercadopago_info()  # Info de MercadoPago
            )
            
            return AuthResponse(
                user=user_response,
                accessToken=access_token,
                refreshToken=refresh_token
            )
            
        except ValueError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(ve)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )
    
    def login_user(self, credentials: UserLogin) -> AuthResponse:
        """Authenticate user and return tokens"""
        print(f"Attempting login for: {credentials.email}")  # Debug log
        
        # Get user by email
        user = self.user_repo.get_by_email(credentials.email)
        if not user:
            raise INVALID_CREDENTIALS_EXCEPTION
        
        # Verify password
        if not verify_password(credentials.password, user.password):
            raise INVALID_CREDENTIALS_EXCEPTION
        
        # Check if user is active
        if not user.isActive:
            raise INACTIVE_USER_EXCEPTION
        
        # Update last login
        self.user_repo.update_last_login(user.id)
        
        # Generate tokens
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id)}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": str(user.id)}
        )
        
        # Convert user to response format with roles
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            phoneNumber=user.phoneNumber,
            documentType=user.documentType.value if user.documentType else None,
            documentId=user.documentId,
            country=user.country,
            city=user.city,
            gender=user.gender.value if user.gender else None,
            profilePhoto=user.get_profile_photo_base64(),
            isActive=user.isActive,
            roles=self._get_user_roles(user),
            createdAt=user.createdAt,
            lastLogin=datetime.utcnow(),  # Current login
            mercadopago=user.get_mercadopago_info()  # Info de MercadoPago
        )
        
        print(f"Login successful for: {user.email}, roles: {user_response.roles}")  # Debug log
        
        return AuthResponse(
            user=user_response,
            accessToken=access_token,
            refreshToken=refresh_token
        )
    
    def refresh_token(self, refresh_token: str) -> Tuple[str, str]:
        """Refresh access token using refresh token"""
        from app.utils.security import verify_token
        
        # Verify refresh token
        payload = verify_token(refresh_token, "refresh")
        user_id = payload.get("user_id")
        email = payload.get("sub")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de actualización inválido"
            )
        
        # Check if user still exists and is active
        user = self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user or not user.isActive:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado o inactivo"
            )
        
        # Generate new tokens
        new_access_token = create_access_token(
            data={"sub": email, "user_id": user_id}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": email, "user_id": user_id}
        )
        
        return new_access_token, new_refresh_token
    
    def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        from app.utils.security import verify_token
        
        # Verify token
        payload = verify_token(token, "access")
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # Get user
        user = self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )
        
        if not user.isActive:
            raise INACTIVE_USER_EXCEPTION
        
        return user
    
    def request_password_reset(self, email: str) -> bool:
        """Request password reset"""
        user = self.user_repo.get_by_email(email)
        if not user:
            # Return True even if user doesn't exist for security
            return True
        
        # Generate reset token
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        # Save token to database
        success = self.user_repo.set_reset_token(email, reset_token, expires_at)
        
        if success:
            # TODO: Send email with reset token
            # self.email_service.send_password_reset_email(user.email, reset_token)
            pass
        
        return success
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        return self.user_repo.reset_password(token, new_password)
    
    def change_password(self, user_id: uuid.UUID, current_password: str, new_password: str) -> bool:
        """Change user password"""
        # Get user
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        # Verify current password
        if not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        # Update password
        return self.user_repo.update_password(user_id, new_password)
    
    def get_user_profile(self, user_id: uuid.UUID) -> Optional[UserResponse]:
        """Get user profile"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            firstName=user.firstName,
            lastName=user.lastName,
            phoneNumber=user.phoneNumber,
            documentType=user.documentType.value if user.documentType else None,
            documentId=user.documentId,
            country=user.country,
            city=user.city,
            gender=user.gender.value if user.gender else None,
            profilePhoto=user.get_profile_photo_base64(),  # Devolver imagen en base64
            isActive=user.isActive,
            roles=self._get_user_roles(user),
            createdAt=user.createdAt,
            lastLogin=user.lastLogin,
            mercadopago=user.get_mercadopago_info()  # Info de MercadoPago
        )
    
    def upload_profile_photo(self, user_id: uuid.UUID, photo_data: bytes, mime_type: str) -> Optional[User]:
        """Upload user profile photo"""
        return self.user_repo.upload_profile_photo(user_id, photo_data, mime_type)
