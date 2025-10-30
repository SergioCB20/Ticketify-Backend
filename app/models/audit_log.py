from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Audit log details (según diagrama)
    action = Column(String(100), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    resource = Column(String(100), nullable=False)  # USER, EVENT, TICKET, etc.
    ipAddress = Column(String(45), nullable=True)  # IPv6 compatible
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    metaData = Column(Text, nullable=True)  # JSON with additional context - CAMBIADO de 'metadata' a 'metaData'
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', resource='{self.resource}')>"
    
    @staticmethod
    def log_action(user_id: uuid.UUID, action: str, resource: str, ip_address: str = None, meta_data: dict = None):
        """Log an action"""
        import json
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ipAddress=ip_address,
            metaData=json.dumps(meta_data) if meta_data else None
        )
        return log
    
    @staticmethod
    def query_logs(user_id: uuid.UUID = None, action: str = None, resource: str = None, start_date = None, end_date = None):
        """Query logs with filters"""
        # Lógica para consultar logs con filtros
        pass
    
    def to_dict(self):
        import json
        return {
            "id": str(self.id),
            "action": self.action,
            "resource": self.resource,
            "ipAddress": self.ipAddress,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metaData": json.loads(self.metaData) if self.metaData else None,
            "userId": str(self.user_id) if self.user_id else None
        }
