from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class TicketTransfer(Base):
    __tablename__ = "ticket_transfers"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Transfer details (según diagrama)
    transferDate = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    oldQR = Column(String, nullable=False)
    newQR = Column(String, nullable=False)
    
    # Foreign keys
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    from_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="transfers")
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="ticket_transfers_from")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="ticket_transfers_to")
    
    def __repr__(self):
        return f"<TicketTransfer(ticket_id='{self.ticket_id}', transferDate='{self.transferDate}')>"
    
    def execute_transfer(self):
        """Execute the transfer"""
        # Invalidar QR anterior y generar nuevo
        self.oldQR = self.ticket.qrCode
        import secrets
        self.newQR = secrets.token_urlsafe(32)
        self.ticket.qrCode = self.newQR
        self.ticket.user_id = self.to_user_id
    
    def notify_parties(self):
        """Notify both parties about the transfer"""
        # Lógica para notificar a ambos usuarios
        pass
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "transferDate": self.transferDate.isoformat() if self.transferDate else None,
            "oldQR": self.oldQR,
            "newQR": self.newQR,
            "ticketId": str(self.ticket_id),
            "fromUserId": str(self.from_user_id),
            "toUserId": str(self.to_user_id)
        }
