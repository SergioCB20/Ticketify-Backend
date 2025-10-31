from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import secrets, string

from app.core.config import settings

# =========================================================
# 🔐 CONFIGURACIÓN GENERAL
# =========================================================
# Corrige la ruta del login en Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================================================
# 🔑 PASSWORDS
# =========================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# =========================================================
# 🧩 JWT TOKENS
# =========================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera token de acceso (por defecto 60 min)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Genera token de refresco (7 días por defecto)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> dict:
    """Decodifica y valida token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(status_code=401, detail="Tipo de token inválido")
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


# =========================================================
# 👤 USUARIO ACTUAL
# =========================================================
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Obtiene el usuario autenticado desde el token"""
    payload = verify_token(token, token_type="access")
    user_id = payload.get("user_id")
    email = payload.get("sub")
    role = payload.get("role")

    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido: falta el user_id")

    return {"id": user_id, "email": email, "role": role}


# =========================================================
# 🔒 UTILIDADES
# =========================================================
def generate_verification_token(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_reset_token() -> str:
    return generate_verification_token(32)

def is_token_expired(token_expires: datetime) -> bool:
    return datetime.now(timezone.utc) > token_expires

def validate_password_strength(password: str) -> dict:
    issues = []
    if len(password) < 8: issues.append("Debe tener al menos 8 caracteres")
    if not any(c.isupper() for c in password): issues.append("Debe tener al menos una mayúscula")
    if not any(c.islower() for c in password): issues.append("Debe tener al menos una minúscula")
    if not any(c.isdigit() for c in password): issues.append("Debe tener al menos un número")
    special_chars = "!@#$%^&*(),.?\":{}|<>"
    if not any(c in special_chars for c in password): issues.append("Se recomienda incluir un carácter especial")
    return {"is_strong": len(issues) == 0, "issues": issues}


# =========================================================
# ⚠️ EXCEPCIONES ESTÁNDAR
# =========================================================
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)

INACTIVE_USER_EXCEPTION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Usuario inactivo"
)

INVALID_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Correo o contraseña incorrectos"
)
