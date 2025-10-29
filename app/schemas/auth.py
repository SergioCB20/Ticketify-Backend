from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRoleEnum(str, Enum):
    ATTENDEE = "ATTENDEE"
    ORGANIZER = "ORGANIZER"

class GenderEnum(str, Enum):
    MALE = "masculino"
    FEMALE = "femenino"
    OTHER = "otro"
    PREFER_NOT_TO_SAY = "prefiero-no-decir"

class DocumentTypeEnum(str, Enum):
    DNI = "DNI"
    CE = "CE"
    PASSPORT = "Pasaporte"

# Request schemas
class UserRegister(BaseModel):
    # Información básica
    email: EmailStr
    password: str = Field(..., min_length=8)
    firstName: str = Field(..., min_length=2, max_length=100, alias="firstName")
    lastName: str = Field(..., min_length=2, max_length=100, alias="lastName")
    
    # Tipo de usuario (NUEVO)
    userType: UserRoleEnum = Field(..., alias="userType")
    
    # Información adicional
    phoneNumber: Optional[str] = Field(None, max_length=20, alias="phoneNumber")
    documentType: DocumentTypeEnum = Field(..., alias="documentType")
    documentId: str = Field(..., min_length=8, max_length=50, alias="documentId")
    
    # Ubicación
    country: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)
    
    # Género
    gender: GenderEnum
    
    # Términos y condiciones
    acceptTerms: bool = Field(..., alias="acceptTerms")
    acceptMarketing: Optional[bool] = Field(False, alias="acceptMarketing")
    
    class Config:
        populate_by_name = True
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('La contraseña debe contener al menos una mayúscula, una minúscula y un número')
        
        return v
    
    @validator('acceptTerms')
    def validate_terms(cls, v):
        """Validate that terms are accepted"""
        if not v:
            raise ValueError('Debes aceptar los términos y condiciones')
        return v
    
    @validator('documentId')
    def validate_document_id(cls, v, values):
        """Validate document ID based on type"""
        doc_type = values.get('documentType')
        
        if doc_type == DocumentTypeEnum.DNI:
            if not v.isdigit() or len(v) != 8:
                raise ValueError('El DNI debe tener exactamente 8 dígitos')
        
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserUpdate(BaseModel):
    firstName: Optional[str] = Field(None, min_length=2, max_length=100)
    lastName: Optional[str] = Field(None, min_length=2, max_length=100)
    phoneNumber: Optional[str] = Field(None, max_length=20)
    profilePhoto: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    
    class Config:
        populate_by_name = True

class ChangePassword(BaseModel):
    currentPassword: str = Field(..., min_length=1, alias="currentPassword")
    newPassword: str = Field(..., min_length=8, alias="newPassword")
    
    class Config:
        populate_by_name = True
    
    @validator('newPassword')
    def validate_new_password(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('La contraseña debe contener al menos una mayúscula, una minúscula y un número')
        
        return v

class PasswordReset(BaseModel):
    token: str
    newPassword: str = Field(..., min_length=8, alias="newPassword")
    
    class Config:
        populate_by_name = True
    
    @validator('newPassword')
    def validate_password(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('La contraseña debe contener al menos una mayúscula, una minúscula y un número')
        
        return v

class ForgotPassword(BaseModel):
    email: EmailStr

# Response schemas
class UserResponse(BaseModel):
    id: str
    email: str
    firstName: str
    lastName: str
    phoneNumber: Optional[str] = None
    documentId: Optional[str] = None
    profilePhoto: Optional[str] = None
    isActive: bool
    roles: List[str] = []  # ✅ AGREGADO: Lista de roles del usuario
    createdAt: datetime
    lastLogin: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class TokenResponse(BaseModel):
    accessToken: str = Field(..., alias="accessToken")
    refreshToken: str = Field(..., alias="refreshToken")
    tokenType: str = Field(default="bearer", alias="tokenType")
    expiresIn: int = Field(..., alias="expiresIn")
    user: UserResponse
    
    class Config:
        populate_by_name = True

class AuthResponse(BaseModel):
    user: UserResponse
    accessToken: str = Field(..., alias="accessToken")
    refreshToken: str = Field(..., alias="refreshToken")
    
    class Config:
        populate_by_name = True

class MessageResponse(BaseModel):
    message: str
    success: bool = True

# Token schemas
class TokenData(BaseModel):
    email: Optional[str] = None
    userId: Optional[str] = Field(None, alias="userId")
    
    class Config:
        populate_by_name = True

class RefreshToken(BaseModel):
    refreshToken: str = Field(..., alias="refreshToken")
    
    class Config:
        populate_by_name = True
