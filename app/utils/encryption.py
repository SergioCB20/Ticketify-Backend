"""
Utilidades para encriptación de datos sensibles
Usado principalmente para tokens de MercadoPago
"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """Servicio de encriptación usando Fernet"""
    
    def __init__(self):
        # En producción, esta key debe venir de variables de entorno
        # y debe ser generada una sola vez y almacenada de forma segura
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """
        Obtener la clave de encriptación de variables de entorno
        Si no existe, genera una nueva (solo para desarrollo)
        
        IMPORTANTE: En producción, esta clave debe:
        1. Generarse UNA SOLA VEZ
        2. Almacenarse de forma segura (AWS Secrets Manager, Azure Key Vault, etc.)
        3. NUNCA cambiar (o perderás acceso a datos ya encriptados)
        """
        try:
            # Intentar obtener de variables de entorno
            if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
                key = settings.ENCRYPTION_KEY.encode()
                if len(key) == 44:  # Fernet keys are 44 bytes
                    return key
            
            # Si no existe, generar una nueva (SOLO DESARROLLO)
            logger.warning("⚠️ Generando nueva clave de encriptación. En producción, usa ENCRYPTION_KEY en .env")
            return Fernet.generate_key()
            
        except Exception as e:
            logger.error(f"Error al obtener clave de encriptación: {str(e)}")
            # Fallback: generar nueva clave
            return Fernet.generate_key()
    
    def encrypt(self, data: str) -> str:
        """
        Encriptar un string
        
        Args:
            data: String a encriptar
        
        Returns:
            String encriptado (base64)
        """
        try:
            if not data:
                return None
            
            # Convertir a bytes y encriptar
            encrypted = self.cipher.encrypt(data.encode())
            
            # Retornar como string base64
            return encrypted.decode()
            
        except Exception as e:
            logger.error(f"Error al encriptar datos: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Desencriptar un string
        
        Args:
            encrypted_data: String encriptado (base64)
        
        Returns:
            String desencriptado
        """
        try:
            if not encrypted_data:
                return None
            
            # Desencriptar
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            
            # Retornar como string
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Error al desencriptar datos: {str(e)}")
            raise


# Instancia global del servicio
encryption_service = EncryptionService()


# ============================================================
# Funciones de utilidad
# ============================================================

def encrypt_mercadopago_token(token: str) -> str:
    """
    Encriptar un token de MercadoPago
    
    Uso:
    ```python
    encrypted = encrypt_mercadopago_token(user.mercadopagoAccessToken)
    user.mercadopagoAccessToken = encrypted
    db.commit()
    ```
    """
    return encryption_service.encrypt(token)


def decrypt_mercadopago_token(encrypted_token: str) -> str:
    """
    Desencriptar un token de MercadoPago
    
    Uso:
    ```python
    decrypted = decrypt_mercadopago_token(user.mercadopagoAccessToken)
    mp_sdk = mercadopago.SDK(decrypted)
    ```
    """
    return encryption_service.decrypt(encrypted_token)


# ============================================================
# Script de migración de tokens existentes
# ============================================================

def migrate_existing_tokens_to_encrypted(db):
    """
    Migrar tokens existentes a formato encriptado
    
    ⚠️ EJECUTAR UNA SOLA VEZ AL IMPLEMENTAR ENCRIPTACIÓN
    
    Uso:
    ```python
    from app.core.database import SessionLocal
    from app.utils.encryption import migrate_existing_tokens_to_encrypted
    
    db = SessionLocal()
    migrate_existing_tokens_to_encrypted(db)
    db.close()
    ```
    """
    from app.models.user import User
    
    logger.info("Iniciando migración de tokens a formato encriptado...")
    
    users_with_tokens = db.query(User).filter(
        User.mercadopagoAccessToken.isnot(None)
    ).all()
    
    encrypted_count = 0
    
    for user in users_with_tokens:
        try:
            # Verificar si el token ya está encriptado
            # (intentar desencriptar, si falla, asumir que está en texto plano)
            try:
                encryption_service.decrypt(user.mercadopagoAccessToken)
                logger.info(f"Usuario {user.email} ya tiene token encriptado")
                continue
            except:
                # Token en texto plano, encriptar
                pass
            
            # Encriptar token de acceso
            if user.mercadopagoAccessToken:
                encrypted_access = encryption_service.encrypt(user.mercadopagoAccessToken)
                user.mercadopagoAccessToken = encrypted_access
            
            # Encriptar token de refresh si existe
            if user.mercadopagoRefreshToken:
                encrypted_refresh = encryption_service.encrypt(user.mercadopagoRefreshToken)
                user.mercadopagoRefreshToken = encrypted_refresh
            
            db.commit()
            encrypted_count += 1
            logger.info(f"✅ Tokens encriptados para usuario {user.email}")
            
        except Exception as e:
            logger.error(f"Error al encriptar tokens para usuario {user.email}: {str(e)}")
            db.rollback()
            continue
    
    logger.info(f"Migración completada. {encrypted_count} usuarios actualizados.")


# ============================================================
# Script para generar nueva clave
# ============================================================

def generate_new_encryption_key() -> str:
    """
    Generar una nueva clave de encriptación Fernet
    
    ⚠️ IMPORTANTE:
    1. Ejecutar UNA SOLA VEZ al configurar el sistema
    2. Guardar la clave generada en variables de entorno
    3. NUNCA compartir o commitear esta clave
    4. NUNCA cambiar esta clave o perderás acceso a datos encriptados
    
    Uso:
    ```bash
    python -c "from app.utils.encryption import generate_new_encryption_key; print(generate_new_encryption_key())"
    ```
    
    Luego agregar a .env:
    ```
    ENCRYPTION_KEY=<clave_generada>
    ```
    """
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    # Generar nueva clave
    print("🔐 Nueva clave de encriptación:")
    print(generate_new_encryption_key())
    print("\n⚠️ IMPORTANTE:")
    print("1. Copia esta clave y agrégala a tu archivo .env como ENCRYPTION_KEY")
    print("2. NUNCA compartas esta clave")
    print("3. NUNCA cambies esta clave después de encriptar datos")
    print("4. Guarda esta clave de forma segura (backup)")
