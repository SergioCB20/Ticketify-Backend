from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import uuid

from app.models.user import User, UserRole
from app.schemas.auth import UserRegister, UserUpdate
from app.utils.security import get_password_hash, generate_verification_token


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
    
    def get_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by verification token"""
        return self.db.query(User).filter(
            and_(
                User.verification_token == token,
                User.verification_token_expires > datetime.utcnow()
            )
        ).first()
    
    def get_by_reset_token(self, token: str) -> Optional[User]:
        """Get user by password reset token"""
        return self.db.query(User).filter(
            and_(
                User.reset_token == token,
                User.reset_token_expires > datetime.utcnow()
            )
        ).first()
    
    def create_user(self, user_data: UserRegister) -> User:
        """Create a new user"""
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Generate verification token
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow().replace(hour=23, minute=59, second=59)  # End of day
        
        # Create user instance
        db_user = User(
            email=user_data.email.lower(),
            first_name=user_data.first_name.strip(),
            last_name=user_data.last_name.strip(),
            hashed_password=hashed_password,
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=False,  # Require email verification
            verification_token=verification_token,
            verification_token_expires=verification_expires
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        # Update only provided fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def update_password(self, user_id: uuid.UUID, new_password: str) -> bool:
        """Update user password"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def verify_email(self, token: str) -> bool:
        """Verify user email using verification token"""
        user = self.get_by_verification_token(token)
        if not user:
            return False
        
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def set_reset_token(self, email: str, token: str, expires_at: datetime) -> bool:
        """Set password reset token for user"""
        user = self.get_by_email(email)
        if not user:
            return False
        
        user.reset_token = token
        user.reset_token_expires = expires_at
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using reset token"""
        user = self.get_by_reset_token(token)
        if not user:
            return False
        
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def update_last_login(self, user_id: uuid.UUID) -> bool:
        """Update user's last login timestamp"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.last_login = datetime.utcnow()
        # Increment login count
        try:
            current_count = int(user.login_count or "0")
            user.login_count = str(current_count + 1)
        except ValueError:
            user.login_count = "1"
        
        self.db.commit()
        
        return True
    
    def deactivate_user(self, user_id: uuid.UUID) -> bool:
        """Deactivate user account"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def activate_user(self, user_id: uuid.UUID) -> bool:
        """Activate user account"""
        user = self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        user.updated_at = datetime.utcnow()
        
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
                User.first_name.ilike(f"%{query}%"),
                User.last_name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        ).offset(skip).limit(limit).all()
    
    def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 20) -> List[User]:
        """Get users by role"""
        return self.db.query(User).filter(User.role == role).offset(skip).limit(limit).all()
    
    def count_users(self) -> int:
        """Get total user count"""
        return self.db.query(User).count()
    
    def count_active_users(self) -> int:
        """Get active user count"""
        return self.db.query(User).filter(User.is_active == True).count()
