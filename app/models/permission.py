from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(code='{self.code}', name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "description": self.description
        }
