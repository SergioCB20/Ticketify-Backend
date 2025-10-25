from sqlalchemy import Column, String, Text, DateTime, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

# Tabla intermedia para relación Many-to-Many Role-Permission
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    users = relationship("User", secondary="user_roles", back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
    def assign_permission(self, permission):
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def revoke_permission(self, permission):
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "updatedAt": self.updatedAt.isoformat() if self.updatedAt else None
        }
