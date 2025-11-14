"""
Utilidad para encriptar/desencriptar datos sensibles usando Fernet (AES-128)

Uso:
    from app.utils.encryption import encrypt_data, decrypt_data
    
    # Encriptar
    encrypted = encrypt_data("my_secret_token")
    
    # Desencriptar
    decrypted = decrypt_data(encrypted)
"""

from cryptography.fernet import Fernet
from app.core.config import settings
from typing import Optional


class EncryptionService:
    """Service for encrypting/decrypting sensitive data"""
    
    def __init__(self):
        """Initialize Fernet cipher with key from settings"""
        if not settings.FERNET_KEY:
            raise ValueError("FERNET_KEY not configured in environment variables")
        
        try:
            self.cipher = Fernet(settings.FERNET_KEY.encode())
        except Exception as e:
            raise ValueError(f"Invalid FERNET_KEY: {str(e)}")
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return ""
        
        try:
            encrypted_bytes = self.cipher.encrypt(data.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted plain text string
        """
        if not encrypted_data:
            return ""
        
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_optional(self, data: Optional[str]) -> Optional[str]:
        """
        Encrypt a string that might be None
        
        Args:
            data: Plain text string or None
            
        Returns:
            Encrypted string or None
        """
        if data is None:
            return None
        return self.encrypt(data)
    
    def decrypt_optional(self, encrypted_data: Optional[str]) -> Optional[str]:
        """
        Decrypt a string that might be None
        
        Args:
            encrypted_data: Encrypted string or None
            
        Returns:
            Decrypted string or None
        """
        if encrypted_data is None:
            return None
        return self.decrypt(encrypted_data)


# Instancia global del servicio
_encryption_service = None

def get_encryption_service() -> EncryptionService:
    """Get singleton instance of EncryptionService"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# Funciones de conveniencia
def encrypt_data(data: str) -> str:
    """Encrypt a string"""
    return get_encryption_service().encrypt(data)


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt a string"""
    return get_encryption_service().decrypt(encrypted_data)


def encrypt_optional(data: Optional[str]) -> Optional[str]:
    """Encrypt a string that might be None"""
    return get_encryption_service().encrypt_optional(data)


def decrypt_optional(encrypted_data: Optional[str]) -> Optional[str]:
    """Decrypt a string that might be None"""
    return get_encryption_service().decrypt_optional(encrypted_data)
