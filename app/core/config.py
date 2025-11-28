import json
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Basic App Config
    APP_NAME: str = "Ticketify"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # URLs
    FRONTEND_URL: str = "https://betting-april-bytes-versus.trycloudflare.com"
    BACKEND_URL: str = "https://unsinuated-shockheaded-chelsie.ngrok-free.dev"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    IMGBB_API_KEY: str
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"] #cambiar en produccion, solo es para que no falle localmente xd (muchos dominios nuevos)

    
    # NGROK
    NGROK_URL: str = ""  # URL de ngrok para desarrollo

    # MercadoPago
    MERCADOPAGO_ACCESS_TOKEN: str
    MERCADOPAGO_PUBLIC_KEY: str
    MERCADOPAGO_SANDBOX: bool = True
    MERCADOPAGO_PRODUCER_TOKEN: str
    
    # MercadoPago OAuth
    MERCADOPAGO_CLIENT_ID: str
    MERCADOPAGO_CLIENT_SECRET: str
    MERCADOPAGO_REDIRECT_URI: str
    MERCADOPAGO_ENVIRONMENT: str = "sandbox"
    
    # Encryption (para tokens de vendedores)
    FERNET_KEY: str

    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "lolmathias16@gmail.com"
    SMTP_PASSWORD: str = "otezitafvbuydsbz"
    EMAIL_FROM: str = "lolmathias16@gmail.com"



    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Validators para listas desde .env
    @field_validator("ALLOWED_HOSTS", "ALLOWED_FILE_TYPES", mode="before")
    def parse_list(cls, v):
        if isinstance(v, str):
            v = v.strip()
            try:
                # intenta parsear JSON
                return json.loads(v)
            except:
                # si no es JSON, asume coma separada
                return [item.strip() for item in v.split(",")]
        return v
    
    @field_validator("MERCADOPAGO_REDIRECT_URI", mode="before")
    def expand_redirect_uri(cls, v, info):
        """Expandir ${NGROK_URL} en MERCADOPAGO_REDIRECT_URI"""
        if isinstance(v, str) and "${NGROK_URL}" in v:
            import os
            ngrok_url = os.getenv("NGROK_URL", "")
            return v.replace("${NGROK_URL}", ngrok_url)
        return v

# Instancia global
settings = Settings()
