from sqlalchemy.orm import Session
from datetime import datetime, timezone
from decimal import Decimal
import uuid

from app.models.purchase import Purchase, PurchaseStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.event import Event
from app.models.user import User

class PurchaseService:

    @staticmethod
    def finalize_purchase_transaction(
        db: Session, 
        purchase: Purchase,
        payment_info: dict
    ) -> bool:
        """
        Finaliza una compra APROBADA por MercadoPago.
        Esta función es llamada por el Webhook.
        
        'payment_info' es un diccionario con datos del pago (ej. id, monto)
        """
        
        # 1. Verificar que no esté ya procesada
        if purchase.status == PurchaseStatus.COMPLETED:
            print(f"La compra {purchase.id} ya fue procesada.")
            return True # Ya se hizo, todo bien.

        if purchase.status != PurchaseStatus.PENDING:
            raise Exception(f"La compra {purchase.id} no está pendiente.")

        # 2. Obtener referencias
        ticket_type = db.query(TicketType).filter(TicketType.id == purchase.ticket_type_id).first()
        if not ticket_type:
            raise Exception("Tipo de ticket no encontrado.")

        # 3. CREAR REGISTRO DE PAGO (Con datos reales de MP)
        payment = Payment(
            amount=Decimal(str(payment_info["amount"])),
            paymentMethod=PaymentMethod.MERCADOPAGO,
            transactionId=str(payment_info["id"]), # ID de pago de MP
            status=PaymentStatus.COMPLETED,
            paymentDate=datetime.now(timezone.utc), # O usar la fecha de MP
            user_id=purchase.user_id
        )
        db.add(payment)
        db.flush()

        # 4. GENERAR LOS TICKETS CON QR
        tickets_created = []
        for i in range(purchase.quantity):
            ticket = Ticket(
                price=ticket_type.price,
                status=TicketStatus.ACTIVE,
                isValid=True,
                user_id=purchase.user_id,
                event_id=purchase.event_id,
                ticket_type_id=purchase.ticket_type_id,
                payment_id=payment.id,
                purchase_id=purchase.id
            )
            db.add(ticket)
            db.flush()
            
            # Generar QR
            ticket.generate_qr() 
            
            tickets_created.append(ticket)
        
        # 5. ACTUALIZAR DISPONIBILIDAD
        ticket_type.quantity_available -= purchase.quantity
        ticket_type.sold_quantity += purchase.quantity
        
        # 6. ACTUALIZAR LA COMPRA
        purchase.status = PurchaseStatus.COMPLETED
        purchase.payment_id = payment.id
        
        # 7. COMMIT DE LA TRANSACCIÓN
        # El webhook debe manejar el try/except y el commit/rollback
        print(f"Compra {purchase.id} finalizada. {len(tickets_created)} tickets creados.")
        
        return True