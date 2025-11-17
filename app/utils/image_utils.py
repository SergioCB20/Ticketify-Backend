"""
Utilidades para manejo de imágenes
Convierte bytes a base64 y procesa fotos de perfil
"""
import base64
from typing import Optional, Any


def bytes_to_base64_url(data: Optional[bytes], mime_type: str = "image/webp") -> Optional[str]:
    """
    Convierte bytes de imagen a data URL base64
    
    Args:
        data: Bytes de la imagen
        mime_type: Tipo MIME de la imagen (default: image/webp)
        
    Returns:
        Data URL en formato base64 o None si no hay datos
        
    Examples:
        >>> photo_bytes = b'\\x89PNG...'
        >>> bytes_to_base64_url(photo_bytes, 'image/png')
        'data:image/png;base64,iVBORw...'
    """
    if data is None:
        return None
    
    if isinstance(data, bytes):
        try:
            base64_string = base64.b64encode(data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_string}"
        except Exception as e:
            print(f"Error converting bytes to base64: {e}")
            return None
    
    # Si ya es string, devolverlo tal cual
    if isinstance(data, str):
        return data
    
    return None


def process_user_photo(user: Any, field_name: str = 'profilePhoto') -> None:
    """
    Procesa la foto de perfil de un usuario en el lugar (in-place)
    Convierte bytes a base64 si es necesario
    
    Args:
        user: Objeto usuario con campo de foto (puede ser modelo SQLAlchemy o dict)
        field_name: Nombre del campo de la foto (default: 'profilePhoto')
        
    Examples:
        >>> user = User(profilePhoto=b'\\x89PNG...')
        >>> process_user_photo(user)
        >>> print(user.profilePhoto)  # 'data:image/webp;base64,...'
    """
    if user is None:
        return
    
    # Manejar objetos con atributos (modelos SQLAlchemy)
    if hasattr(user, field_name):
        photo = getattr(user, field_name)
        if photo and isinstance(photo, bytes):
            converted = bytes_to_base64_url(photo)
            setattr(user, field_name, converted)
    
    # Manejar diccionarios
    elif isinstance(user, dict) and field_name in user:
        photo = user[field_name]
        if photo and isinstance(photo, bytes):
            user[field_name] = bytes_to_base64_url(photo)


def process_user_photos_list(users: list, field_name: str = 'profilePhoto') -> None:
    """
    Procesa las fotos de una lista de usuarios
    
    Args:
        users: Lista de usuarios
        field_name: Nombre del campo de la foto
        
    Examples:
        >>> users = [User(profilePhoto=b'...'), User(profilePhoto=b'...')]
        >>> process_user_photos_list(users)
    """
    if not users:
        return
    
    for user in users:
        process_user_photo(user, field_name)


def process_nested_user_photo(obj: Any, user_field: str, photo_field: str = 'profilePhoto') -> None:
    """
    Procesa la foto de un usuario anidado en otro objeto
    Útil para objetos como MarketplaceListing que tienen un campo 'seller'
    
    Args:
        obj: Objeto que contiene un usuario anidado
        user_field: Nombre del campo que contiene el usuario (ej: 'seller', 'buyer', 'user')
        photo_field: Nombre del campo de foto en el usuario (default: 'profilePhoto')
        
    Examples:
        >>> listing = MarketplaceListing(seller=User(profilePhoto=b'...'))
        >>> process_nested_user_photo(listing, 'seller')
        >>> print(listing.seller.profilePhoto)  # 'data:image/webp;base64,...'
    """
    if obj is None:
        return
    
    # Manejar objetos con atributos
    if hasattr(obj, user_field):
        user = getattr(obj, user_field)
        if user:
            process_user_photo(user, photo_field)
    
    # Manejar diccionarios
    elif isinstance(obj, dict) and user_field in obj:
        user = obj[user_field]
        if user:
            process_user_photo(user, photo_field)
