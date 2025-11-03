from typing import Optional, List
from sqlalchemy import and_, or_
from datetime import datetime
import uuid

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
            isActive=True
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
        """Update user information"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        # Get update data
        update_data = user_data.dict(exclude_unset=True)
        
        # If email is being updated, check it's not taken by another user
        if 'email' in update_data and update_data['email']:
            new_email = update_data['email'].lower()
            # Check if another user has this email
            existing_user = self.get_by_email(new_email)
            if existing_user and existing_user.id != user_id:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo electrónico ya está registrado por otro usuario"
                )
            update_data['email'] = new_email
        
        # Update only provided fields
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
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
        
        user.login()
        
        self.db.commit()
        
        return True
    
    def set_reset_token(self, email: str, token: str, expires_at: datetime) -> bool:
        """Set password reset token for user"""
        user = self.get_by_email(email)
        if not user:
            return False
        
        self.db.commit()
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using reset token"""
        return False
    
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
