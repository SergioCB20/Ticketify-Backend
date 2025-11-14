"""
Models Package
Importa todos los modelos de la aplicación
"""

# Core models
from app.models.user import User, UserRole, AdminRole, user_roles, DocumentType, Gender
from app.models.role import Role, role_permissions
from app.models.permission import Permission

# Event models
from app.models.event import Event, EventStatus
from app.models.event_category import EventCategory
from app.models.event_schedule import EventSchedule

# Ticket models
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.ticket_transfer import TicketTransfer

# Payment models
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.models.purchase import Purchase
# Promotion model
from app.models.promotion import Promotion

# Marketplace
from app.models.marketplace_listing import MarketplaceListing, ListingStatus

# Validation models
from app.models.validation import Validation
from app.models.qr_validation_log import QRValidationLog

# Support models
from app.models.dispute import Dispute, DisputeType, DisputeStatus
from app.models.support_ticket import SupportTicket

# Notification
from app.models.notification import Notification, NotificationType, NotificationChannel

# Analytics and reporting
from app.models.analytics import Analytics
from app.models.report import Report
from app.models.audit_log import AuditLog

__all__ = [
    # Core
    "User",
    "UserRole",
    "AdminRole",
    "user_roles",
    "DocumentType",
    "Gender",
    "Role",
    "role_permissions",
    "Permission",
    
    # Events
    "Event",
    "EventStatus",
    "EventCategory",
    "EventSchedule",
    
    # Tickets
    "Ticket",
    "TicketStatus",
    "TicketType",
    "TicketTransfer",
    
    # Payments
    "Payment",
    "PaymentStatus",
    "PaymentMethod",
    "Transaction",
    "TransactionType",
    "TransactionStatus",
    "Purchase",
    "Promotion",
    
    # Marketplace
    "MarketplaceListing",
    "ListingStatus",
    
    # Validation
    "Validation",
    "QRValidationLog",
    
    # Support
    "Dispute",
    "DisputeType",
    "DisputeStatus",
    "SupportTicket",
    
    # Notifications
    "Notification",
    "NotificationType",
    "NotificationChannel",
    
    # Analytics
    "Analytics",
    "Report",
    "AuditLog",
]
