from datetime import datetime, timedelta, timezone
from typing import Union, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import string
import time

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Usar timestamp en lugar de datetime
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # Debug log
    print(f"[DEBUG] Token created with expiry: {expire} (in {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes)")
    print(f"[DEBUG] Current UTC time: {datetime.utcnow()}")
    
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token (longer expiry)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)  # 7 days for refresh token
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode JWT token"""
    try:
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Debug logs
        exp = payload.get("exp")
        current_timestamp = int(datetime.utcnow().timestamp())
        
        print(f"[DEBUG] Token type: {payload.get('type')}")
        print(f"[DEBUG] Token exp timestamp: {exp}")
        print(f"[DEBUG] Current timestamp: {current_timestamp}")
        print(f"[DEBUG] Time until expiry: {exp - current_timestamp} seconds")
        
        # Check token type
        if payload.get("type") != token_type:
            print(f"[DEBUG] Token type mismatch. Expected: {token_type}, Got: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token type mismatch"
            )
        
        # Check expiration - jwt library already checks this, but we can add custom logic
        if exp and current_timestamp > exp:
            print(f"[DEBUG] Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        print(f"[DEBUG] Token validated successfully for user: {payload.get('sub')}")
        return payload
    
    except jwt.ExpiredSignatureError:
        print(f"[DEBUG] JWT ExpiredSignatureError caught")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    
    except JWTError as e:
        print(f"[DEBUG] JWTError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

def generate_verification_token(length: int = 32) -> str:
    """Generate a secure random token for email verification or password reset"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_reset_token() -> str:
    """Generate password reset token"""
    return generate_verification_token(32)

def is_token_expired(token_expires: datetime) -> bool:
    """Check if a token has expired"""
    return datetime.utcnow() > token_expires

def validate_password_strength(password: str) -> dict:
    """Validate password strength and return feedback"""
    issues = []
    
    if len(password) < 8:
        issues.append("Debe tener al menos 8 caracteres")
    
    if not any(c.isupper() for c in password):
        issues.append("Debe contener al menos una letra mayúscula")
    
    if not any(c.islower() for c in password):
        issues.append("Debe contener al menos una letra minúscula")
    
    if not any(c.isdigit() for c in password):
        issues.append("Debe contener al menos un número")
    
    # Optional: Check for special characters
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password):
        issues.append("Se recomienda incluir al menos un carácter especial")
    
    return {
        "is_strong": len(issues) == 0,
        "issues": issues
    }

# Security constants
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

INACTIVE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Inactive user"
)

INVALID_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password"
)
