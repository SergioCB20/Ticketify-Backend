from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Report details (según diagrama)
    type = Column(String(100), nullable=False)  # SALES, EVENTS, USERS, FINANCIAL, etc.
    generatedAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    data = Column(Text, nullable=True)  # JSON data with report results
    
    # Foreign key
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(type='{self.type}', generatedAt='{self.generatedAt}')>"
    
    def generate_report(self, report_data: dict):
        """Generate report with data"""
        import json
        self.data = json.dumps(report_data)
        self.generatedAt = func.now()
    
    def export_to_pdf(self):
        """Export report to PDF"""
        # Lógica para exportar a PDF
        pass
    
    def to_dict(self):
        import json
        return {
            "id": str(self.id),
            "type": self.type,
            "generatedAt": self.generatedAt.isoformat() if self.generatedAt else None,
            "data": json.loads(self.data) if self.data else None,
            "generatedBy": str(self.generated_by)
        }
