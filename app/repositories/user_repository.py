from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import and_, or_, func
from datetime import datetime, timezone
import re
import base64
import uuid
from typing import Optional
from fastapi import HTTPException, status
from app.models.user import User, AdminRole
from app.schemas.auth import UserUpdate

from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import UserRegister, UserUpdate
from app.utils.security import get_password_hash


class UserRepository:
    """Repository for User database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    def get_by_document_id(self, document_id: str) -> Optional[User]:
        """Get user by document ID"""
        return self.db.query(User).filter(User.documentId == document_id).first()

    def get_by_id_with_role(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID, and eagerly load the user's role relationship"""
        return self.db.query(User).options(joinedload(User.roles)).filter(User.id == user_id).first()

    # --- NUEVO MÉTODO AUXILIAR ---
    def get_by_reset_token(self, token: str) -> Optional[User]:
        """Get user by password reset token"""
        return self.db.query(User).filter(User.resetToken == token).first()
    # --- FIN NUEVO MÉTODO ---
    
    def create_user(self, user_data: UserRegister) -> User:
        """Create a new user"""
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Import enums from models
        from app.models.user import DocumentType, Gender
        
        # Create user instance
        db_user = User(
            email=user_data.email.lower(),
            password=hashed_password,
            firstName=user_data.firstName.strip(),
            lastName=user_data.lastName.strip(),
            phoneNumber=user_data.phoneNumber,
            documentType=DocumentType(user_data.documentType.value),
            documentId=user_data.documentId,
            country=user_data.country,
            city=user_data.city,
            gender=Gender(user_data.gender.value),
            isActive=True,
            emailNotifications=user_data.acceptMarketing if user_data.acceptMarketing is not None else False
        )
        
        self.db.add(db_user)
        self.db.flush()  # Flush to get the user ID
        
        # Assign role based on userType
        role_name = user_data.userType.value
        role = self.db.query(Role).filter(Role.name == role_name).first()
        
        if role:
            db_user.roles.append(role)
        else:
            # If role doesn't exist, create it
            new_role = Role(
                name=role_name,
                description=f"{role_name} role"
            )
            self.db.add(new_role)
            self.db.flush()
            db_user.roles.append(new_role)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        """Actualiza la información del usuario y almacena la foto directamente en base64"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        # Obtener datos a actualizar
        update_data = user_data.model_dump(exclude_unset=True)

    # Manejar profilePhoto si viene en base64
        if 'profilePhoto' in update_data:
            profile_photo_base64 = update_data.pop('profilePhoto')

            if profile_photo_base64 is None:
                # Eliminar foto
                user.profilePhoto = None
                user.profilePhotoMimeType = None
            elif profile_photo_base64.startswith('data:image/'):
                # Extraer MIME type y datos base64
                match = re.match(r'data:(image/[\w+]+);base64,(.+)', profile_photo_base64)
                if match:
                    mime_type = match.group(1)
                    base64_data = match.group(2)

                try:
                    # Decodificar base64 a bytes
                    photo_bytes = base64.b64decode(base64_data)

                    # Validar tamaño (máx. 5 MB)
                    if len(photo_bytes) > 5 * 1024 * 1024:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="La imagen es demasiado grande. Tamaño máximo: 5MB"
                        )

                    # Guardar la imagen directamente como base64 en la DB
                    user.profilePhoto = photo_bytes
                    user.profilePhotoMimeType = mime_type

                except ValueError as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Imagen base64 inválida: {str(e)}"
                    )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Formato de imagen no soportado"
                )

    # Validar email si se actualiza
        if 'email' in update_data and update_data['email']:
            new_email = update_data['email'].lower()
            existing_user = self.get_by_email(new_email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está registrado por otro usuario"
                )
            update_data['email'] = new_email

        # Actualizar campos normales
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    # --- NUEVO MÉTODO GENÉRICO REQUERIDO POR ADMINSERVICE ---
    def update(self, user: User, data: Dict[str, Any]) -> User:
        """Actualización genérica de campos de usuario"""
        for field, value in data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    # --- FIN NUEVO MÉTODO ---
    
    def update_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """Update user password"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.password = get_password_hash(new_password)
        
        self.db.commit()
        
        return True
    
    def update_last_login(self, user_id: uuid.UUID) -> bool:
        """Update user's last login timestamp"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.login() # Llama al método del modelo
        
        self.db.commit()
        
        return True
    
    
    # --- MÉTODO CORREGIDO ---
    def set_reset_token(self, email: str, token: str, expires_at: datetime) -> bool:
        """Set password reset token for user"""
        user = self.get_by_email(email)
        if not user:
            return False
        
        # Asigna el token y la expiración al modelo
        user.resetToken = token
        user.resetTokenExpires = expires_at
        
        self.db.commit()
        
        return True
    # --- FIN CORRECCIÓN ---
    
    # --- MÉTODO CORREGIDO ---
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using reset token"""
        
        # 1. Encontrar al usuario por el token
        user = self.get_by_reset_token(token)
        if not user:
            return False # Token no encontrado
        
        # 2. Verificar que el token no haya expirado
        # (Usamos timezone.utc para comparar correctamente)
        if user.resetTokenExpires is None or user.resetTokenExpires < datetime.now(timezone.utc):
            return False # Token expirado
        
        # 3. Actualizar contraseña y anular el token
        user.password = get_password_hash(new_password)
        user.resetToken = None
        user.resetTokenExpires = None
        
        self.db.commit()
        
        return True
    # --- FIN CORRECCIÓN ---
    
    def deactivate_user(self, user_id: uuid.UUID) -> bool:
        """Deactivate user account"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.isActive = False
        
        self.db.commit()
        
        return True
    
    def activate_user(self, user_id: uuid.UUID) -> bool:
        """Activate user account"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.isActive = True
        
        self.db.commit()
        
        return True
    
    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete user account permanently"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    def get_all_users(self, skip: int = 0, limit: int = 20) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def search_users(self, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        """Search users by name or email"""
        return self.db.query(User).filter(
            or_(
                User.firstName.ilike(f"%{query}%"),
                User.lastName.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit).all()
    
    def count_users(self) -> int:
        """Get total user count"""
        return self.db.query(User).count()
    
    def count_active_users(self) -> int:
        """Get active user count"""
        return self.db.query(User).filter(User.isActive == True).count()

    # --- MÉTODOS REQUERIDOS POR ADMINSERVICE ---

    def _get_admin_role_names(self) -> List[str]:
        """Helper para obtener la lista de nombres de roles de admin"""
        return [r.value for r in AdminRole]

    def get_non_admin_users_paginated(
        self,
        page: int,
        page_size: int,
        search: Optional[str],
        is_active: Optional[bool]
    ) -> Tuple[List[User], int]:
        """Obtener usuarios paginados que NO son administradores"""
        
        admin_role_names = self._get_admin_role_names()
        
        # Query base: excluye admins
        query = self.db.query(User).outerjoin(User.roles).filter(
            ~User.roles.any(Role.name.in_(admin_role_names))
        )
        
        # Aplicar filtros
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.firstName.ilike(f"%{search}%"),
                User.lastName.ilike(f"%{search}%"),
                User.documentId.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if is_active is not None:
            query = query.filter(User.isActive == is_active)
        
        # Contar total ANTES de paginar
        total = query.count()
        
        # Calcular paginación
        offset = (page - 1) * page_size
        
        # Obtener usuarios
        users = query.order_by(User.createdAt.desc()).offset(offset).limit(page_size).all()
        
        return users, total

    def get_all_admins(self) -> List[User]:
        """Obtener todos los usuarios que SÍ son administradores"""
        admin_role_names = self._get_admin_role_names()
        
        admins = self.db.query(User).join(User.roles).filter(
            Role.name.in_(admin_role_names)
        ).distinct().all()
        
        return admins

    def count_non_admins(self, is_active: Optional[bool] = None) -> int:
        """Contar usuarios que NO son administradores"""
        admin_role_names = self._get_admin_role_names()
        query = self.db.query(func.count(User.id)).outerjoin(User.roles).filter(
            ~User.roles.any(Role.name.in_(admin_role_names))
        )
        if is_active is not None:
            query = query.filter(User.isActive == is_active)
        
        return query.scalar() or 0

    def count_admins(self, is_active: Optional[bool] = None) -> int:
        """Contar usuarios que SÍ son administradores"""
        admin_role_names = self._get_admin_role_names()
        query = self.db.query(func.count(User.id.distinct())).join(User.roles).filter(
            Role.name.in_(admin_role_names)
        )
        if is_active is not None:
            query = query.filter(User.isActive == is_active)
            
        return query.scalar() or 0

    def count_new_users_since(self, date: datetime) -> int:
        """Contar usuarios registrados desde una fecha específica"""
        return self.db.query(func.count(User.id)).filter(
            User.createdAt >= date
        ).scalar() or 0