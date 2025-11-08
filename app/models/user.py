from sqlalchemy import Column, String, Boolean, DateTime, Enum, Table, ForeignKey, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

# Enums actualizados según diagrama
class UserRole(str, enum.Enum):
    ATTENDEE = "ATTENDEE"  # Cliente/Asistente
    ORGANIZER = "ORGANIZER"  # Organizador

class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    CONTENT_ADMIN = "CONTENT_ADMIN"

class DocumentType(str, enum.Enum):
    DNI = "DNI"
    CE = "CE"
    PASSPORT = "Pasaporte"

class Gender(str, enum.Enum):
    MALE = "masculino"
    FEMALE = "femenino"
    OTHER = "otro"
    PREFER_NOT_TO_SAY = "prefiero-no-decir"

# Tabla intermedia para relación Many-to-Many User-Role
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Basic information (según diagrama)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Renombrado de hashed_password
    firstName = Column(String(100), nullable=False)  # Renombrado de first_name
    lastName = Column(String(100), nullable=False)  # Renombrado de last_name
    phoneNumber = Column(String(20), nullable=True)  # NUEVO
    documentId = Column(String(50), nullable=True)  # NUEVO
    # Document information
    documentType = Column(Enum(DocumentType), nullable=True)  # DNI, CE, Pasaporte
    documentId = Column(String(50), nullable=True, unique=True, index=True)  # Número de documento
    
    # Location
    country = Column(String(100), nullable=True)  # País
    city = Column(String(100), nullable=True)  # Ciudad
    
    # Personal
    gender = Column(Enum(Gender), nullable=True)  # Género
    profilePhoto = Column(LargeBinary, nullable=True)  
    profilePhotoMimeType = Column(String(50), nullable=True)  # Tipo MIME (image/jpeg, image/png, etc.)
    # Status
    isActive = Column(Boolean, default=True, nullable=False)  # Renombrado de is_active
    
    # Timestamps
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    lastLogin = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    organized_events = relationship("Event", back_populates="organizer", foreign_keys="Event.organizer_id")
    tickets = relationship("Ticket", foreign_keys="Ticket.user_id", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    marketplace_listings = relationship("MarketplaceListing", foreign_keys="MarketplaceListing.seller_id", back_populates="seller")
    transactions = relationship("Transaction", back_populates="user")
    disputes_reported = relationship("Dispute", foreign_keys="Dispute.reported_by", back_populates="reporter")
    disputes_assigned = relationship("Dispute", foreign_keys="Dispute.assigned_admin", back_populates="admin")
    support_tickets = relationship("SupportTicket", foreign_keys="SupportTicket.user_id", back_populates="user")
    support_tickets_assigned = relationship("SupportTicket", foreign_keys="SupportTicket.assigned_to", back_populates="admin")
    reports = relationship("Report", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    ticket_transfers_from = relationship("TicketTransfer", foreign_keys="TicketTransfer.from_user_id", back_populates="from_user")
    ticket_transfers_to = relationship("TicketTransfer", foreign_keys="TicketTransfer.to_user_id", back_populates="to_user")
    created_promotions = relationship("Promotion", back_populates="created_by")
    purchases = relationship("Purchase", back_populates="user")
    def __repr__(self):
        return f"<User(email='{self.email}')>"
    
    @property
    def full_name(self):
        return f"{self.firstName} {self.lastName}"
    
    def register(self):
        """Register new user"""
        self.createdAt = func.now()
        self.isActive = True
    
    def login(self):
        """Update last login timestamp"""
        from datetime import datetime
        self.lastLogin = datetime.utcnow()
    
    def update_profile(self, **kwargs):
        """Update user profile"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def upload_photo(self, photo_data: bytes, mime_type: str):
        """Upload profile photo as binary data"""
        self.profilePhoto = photo_data
        self.profilePhotoMimeType = mime_type
    
    def get_profile_photo_base64(self) -> str | None:
        """Get profile photo as base64 string for JSON response"""
        if self.profilePhoto:
            import base64
            encoded = base64.b64encode(self.profilePhoto).decode('utf-8')
            return f"data:{self.profilePhotoMimeType or 'image/jpeg'};base64,{encoded}"
        return None
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "email": self.email,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "phoneNumber": self.phoneNumber,
            "documentType": self.documentType.value if self.documentType else None,
            "documentId": self.documentId,
            "country": self.country,
            "city": self.city,
            "gender": self.gender.value if self.gender else None,
            "profilePhoto": self.get_profile_photo_base64(),
            "isActive": self.isActive,
            "createdAt": self.createdAt.isoformat() if self.createdAt else None,
            "lastLogin": self.lastLogin.isoformat() if self.lastLogin else None,
            "fullName": self.full_name
        }
