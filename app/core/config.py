from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Basic App Config
    APP_NAME: str = "Ticketify"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # Database
    DATABASE_URL: str = "postgresql://ticketify_user:password@localhost:5432/ticketify_db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000"]
    
    # MercadoPago
    MERCADOPAGO_ACCESS_TOKEN: str = ""
    MERCADOPAGO_PUBLIC_KEY: str = ""
    MERCADOPAGO_SANDBOX: bool = True  # Para desarrollo
    
    # Email Configuration
    SMTP_SERVER: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@ticketify.com"
    
    # Redis (para cache y Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()