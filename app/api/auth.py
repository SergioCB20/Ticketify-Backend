from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import io
from PIL import Image

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_user, get_optional_current_user
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister, UserLogin, AuthResponse, UserResponse, 
    MessageResponse, RefreshToken, ChangePassword, 
    ForgotPassword, PasswordReset, UserUpdate, GoogleLoginRequest
)
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/google/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def google_login(
    data: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """Endpoint para manejar el login con Google de usuarios YA REGISTRADOS."""
    auth_service = AuthService(db)
    # La función del servicio ahora se llama login_with_google
    return auth_service.login_with_google(data)

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters with uppercase, lowercase, and number
    - **firstName**: User's first name
    - **lastName**: User's last name
    - **phoneNumber**: Contact phone number
    - **documentType**: DNI, CE, or Pasaporte
    - **documentId**: Document ID number
    - **country**: Country of residence
    - **city**: City of residence
    - **gender**: Gender selection
    - **acceptTerms**: Must be true to register
    - **acceptMarketing**: Optional marketing consent
    """
    auth_service = AuthService(db)
    return auth_service.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
async def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login user with email and password
    
    Returns access token and refresh token for authentication
    """
    auth_service = AuthService(db)
    return auth_service.login_user(credentials)

@router.post("/refresh", response_model=dict)
async def refresh_access_token(
    refresh_data: RefreshToken,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    Returns new access token and refresh token
    """
    auth_service = AuthService(db)
    access_token, refresh_token = auth_service.refresh_token(refresh_data.refreshToken)
    
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "bearer"
    }

@router.post("/logout", response_model=MessageResponse)
async def logout_user():
    """
    Logout current user (client-side token invalidation)
    
    In JWT stateless approach, logout is mainly client-side.
    This endpoint always returns success, even with expired tokens,
    as the client will clear the tokens locally.
    """
    return MessageResponse(
        message="Sesión cerrada exitosamente",
        success=True
    )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    
    Returns authenticated user information
    """
    # Get user roles
    roles = [role.name for role in current_user.roles] if current_user.roles else []
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        firstName=current_user.firstName,
        lastName=current_user.lastName,
        phoneNumber=current_user.phoneNumber,
        documentType=current_user.documentType.value if current_user.documentType else None,
        documentId=current_user.documentId,
        country=current_user.country,
        city=current_user.city,
        gender=current_user.gender.value if current_user.gender else None,
        profilePhoto=current_user.get_profile_photo_base64(),
        isActive=current_user.isActive,
        roles=roles,
        createdAt=current_user.createdAt,
        lastLogin=current_user.lastLogin,
        mercadopago=current_user.get_mercadopago_info()  # Info de MercadoPago
    )

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    
    Only provided fields will be updated. You can update:
    - email: New email address (must be unique)
    - firstName: First name
    - lastName: Last name
    - phoneNumber: Phone number
    - country: Country of residence
    - city: City of residence
    - gender: Gender (masculino, femenino, otro, prefiero-no-decir)
    - profilePhoto: Profile photo base64
    
    Note: If you change your email, you'll need to verify it again.
    """

    from app.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    updated_user = user_repo.update_user(current_user.id, user_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar el perfil"
        )
    
    # Get user roles
    roles = [role.name for role in updated_user.roles] if updated_user.roles else []
    
    return UserResponse(
        id=str(updated_user.id),
        email=updated_user.email,
        firstName=updated_user.firstName,
        lastName=updated_user.lastName,
        phoneNumber=updated_user.phoneNumber,
        documentType=updated_user.documentType.value if updated_user.documentType else None,
        documentId=updated_user.documentId,
        country=updated_user.country,
        city=updated_user.city,
        gender=updated_user.gender.value if updated_user.gender else None,
        profilePhoto=updated_user.get_profile_photo_base64(),
        isActive=updated_user.isActive,
        roles=roles,
        createdAt=updated_user.createdAt,
        lastLogin=updated_user.lastLogin,
        mercadopago=updated_user.get_mercadopago_info()  # Info de MercadoPago
    )

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Requires current password for verification
    """
    auth_service = AuthService(db)
    success = auth_service.change_password(
        current_user.id, 
        password_data.currentPassword, 
        password_data.newPassword
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al cambiar la contraseña"
        )
    
    return MessageResponse(
        message="Contraseña cambiada exitosamente",
        success=True
    )

@router.post("/forgot-password", response_model=MessageResponse)
async def request_password_reset(
    reset_data: ForgotPassword,
    db: Session = Depends(get_db)
):
    """
    Request password reset
    
    Sends password reset instructions to email if it exists
    """
    auth_service = AuthService(db)
    auth_service.request_password_reset(reset_data.email)
    
    # Always return success for security reasons
    return MessageResponse(
        message="Si el correo existe, recibirás instrucciones para restablecer tu contraseña",
        success=True
    )

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Reset password using reset token
    
    Token must be valid and not expired
    """
    auth_service = AuthService(db)
    success = auth_service.reset_password(reset_data.token, reset_data.newPassword)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    return MessageResponse(
        message="Contraseña restablecida exitosamente",
        success=True
    )

@router.delete("/account", response_model=MessageResponse)
async def delete_user_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user account
    
    Permanently deletes the user account and all associated data
    """
    from app.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    success = user_repo.delete_user(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al eliminar la cuenta"
        )
    
    return MessageResponse(
        message="Cuenta eliminada exitosamente",
        success=True
    )

@router.post("/upload-photo", response_model=dict)
async def upload_profile_photo(
    file: UploadFile = File(..., description="Imagen (JPEG/PNG/GIF/WEBP - Máx 5MB)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload profile photo (alternative to PUT /profile with base64)
    
    **Accepted formats:** JPEG, PNG, GIF, WEBP
    **Max size:** 5MB
    
    **Processing:**
    - Images >800x800px are automatically resized
    - Stored as BLOB in PostgreSQL
    - Returns base64 string
    
    **Response:**
    ```json
    {
      "message": "Foto subida exitosamente",
      "photoUrl": "data:image/jpeg;base64,..."
    }
    ```
    """
    # Validar tipo de archivo
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido. Solo JPEG, PNG, GIF, WEBP."
        )
    
    # Leer contenido
    contents = await file.read()
    
    # Validar tamaño (5MB)
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Archivo demasiado grande. Máximo: 5MB"
        )
    
    # Validar imagen con Pillow
    try:
        image = Image.open(io.BytesIO(contents))
        image.verify()
        
        # Reabrir para procesar
        image = Image.open(io.BytesIO(contents))
        
        # Redimensionar si es necesario
        max_size = (800, 800)
        if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Guardar redimensionada
            img_byte_arr = io.BytesIO()
            image_format = image.format or 'JPEG'
            image.save(img_byte_arr, format=image_format)
            contents = img_byte_arr.getvalue()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Imagen inválida: {str(e)}"
        )
    
    # Subir usando el servicio
    auth_service = AuthService(db)
    updated_user = auth_service.upload_profile_photo(
        current_user.id,
        contents,
        file.content_type
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al subir la foto"
        )
    
    return {
        "message": "Foto de perfil subida exitosamente",
        "photoUrl": updated_user.get_profile_photo_base64()
    }
