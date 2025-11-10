import requests
from typing import Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository


class MercadoPagoOAuthService:
    """Service for handling MercadoPago OAuth 2.0 flow"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        
        # MercadoPago OAuth endpoints
        self.auth_url = "https://auth.mercadopago.com.pe/authorization"
        self.token_url = "https://api.mercadopago.com/oauth/token"
        self.user_info_url = "https://api.mercadopago.com/users/me"
        
        # Configuración desde .env
        self.client_id = settings.MERCADOPAGO_CLIENT_ID
        self.client_secret = settings.MERCADOPAGO_CLIENT_SECRET
        self.redirect_uri = settings.MERCADOPAGO_REDIRECT_URI
    
    def get_authorization_url(self, user_id: str) -> str:
        """Generate MercadoPago OAuth authorization URL with forced logout"""
        import time
        from urllib.parse import quote
        
        # Parámetros OAuth
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "platform_id": "mp",
            "state": user_id,
            "redirect_uri": self.redirect_uri,
            "_t": str(int(time.time()))  # Timestamp para evitar cache
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        oauth_url = f"{self.auth_url}?{query_string}"
        
        # Forzar logout de MercadoLibre/MercadoPago antes de OAuth
        # Esto permite al usuario elegir qué cuenta vincular
        logout_url = f"https://mercadolibre.com/jms/mpe/lgz/logout?go={quote(oauth_url)}"
        
        return logout_url
    
    def exchange_code_for_tokens(self, code: str) -> Dict:
        """Exchange authorization code for access and refresh tokens"""
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        try:
            response = requests.post(self.token_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
                "user_id": str(data["user_id"]),
                "public_key": data.get("public_key", ""),
                "live_mode": data.get("live_mode", False)
            }
        
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al intercambiar código por tokens: {str(e)}"
            )
    
    def get_user_info(self, access_token: str) -> Dict:
        """Get MercadoPago user information"""
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "email": data.get("email"),
                "nickname": data.get("nickname"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "country_id": data.get("country_id")
            }
        
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al obtener información del usuario MP: {str(e)}"
            )
    
    def connect_account(self, user_id: uuid.UUID, code: str) -> User:
        """Complete OAuth flow: exchange code and save tokens"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        token_data = self.exchange_code_for_tokens(code)
        user_info = self.get_user_info(token_data["access_token"])
        
        # Verificar si esta cuenta de MP ya está vinculada a otro usuario
        existing_mp_user = self.db.query(User).filter(
            User.mercadopagoUserId == token_data["user_id"],
            User.id != user_id
        ).first()
        
        if existing_mp_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="account_already_linked"
            )
        
        user.connect_mercadopago(
            user_id=token_data["user_id"],
            public_key=token_data["public_key"],
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            expires_in=token_data["expires_in"],
            email=user_info["email"]
        )
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def disconnect_account(self, user_id: uuid.UUID) -> bool:
        """Disconnect MercadoPago account"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        if not user.isMercadopagoConnected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No tienes una cuenta de MercadoPago vinculada"
            )
        
        user.disconnect_mercadopago()
        self.db.commit()
        
        return True
    
    def get_connection_status(self, user_id: uuid.UUID) -> Dict:
        """Get MercadoPago connection status for user"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return user.get_mercadopago_info() or {
            "isConnected": False,
            "email": None,
            "connectedAt": None,
            "tokenExpired": None
        }
    
    def refresh_access_token(self, user_id: uuid.UUID) -> User:
        """Refresh expired access token using refresh token (with decryption)"""
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.isMercadopagoConnected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario no tiene cuenta de MercadoPago vinculada"
            )
        
        # Desencriptar refresh token
        refresh_token = user.get_decrypted_refresh_token()
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token no disponible o corrupto"
            )
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        try:
            response = requests.post(self.token_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Actualizar con nuevos tokens encriptados
            from datetime import datetime, timedelta, timezone
            from app.utils.encryption import encrypt_data
            
            user.mercadopagoAccessToken = encrypt_data(data["access_token"])
            user.mercadopagoRefreshToken = encrypt_data(data["refresh_token"])
            user.mercadopagoTokenExpires = datetime.now(timezone.utc) + timedelta(seconds=data["expires_in"])
            
            self.db.commit()
            self.db.refresh(user)
            
            return user
        
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al refrescar token: {str(e)}"
            )
