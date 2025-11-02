from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from uuid import UUID
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_transfer import TicketTransfer
from app.models.user import User

class MarketplaceService:

    def __init__(self, db: Session):
        self.db = db

    def transfer_ticket_on_purchase(
        self,
        listing: MarketplaceListing,
        buyer: User,
        payment_id: UUID # El ID del nuevo pago
    ) -> Ticket:
        """
        Esta es la función CRÍTICA que garantiza la validez.
        Se ejecuta DESPUÉS de que el pago del comprador ha sido confirmado.
        """
        
        # 1. Obtener el ticket original que estaba a la venta
        original_ticket = listing.ticket
        if not original_ticket:
            raise Exception("No se encontró el ticket original asociado al listado.")

        # 2. Marcar el listado de reventa como VENDIDO
        listing.status = ListingStatus.SOLD
        listing.buyer_id = buyer.id
        listing.sold_at = datetime.utcnow()
        self.db.add(listing)

        # 3. Invalidar el ticket original (del vendedor)
        original_ticket_qr = original_ticket.qrCode
        original_ticket.status = TicketStatus.TRANSFERRED
        original_ticket.isValid = False
        self.db.add(original_ticket)
        
        # 4. Crear el NUEVO ticket para el comprador
        new_ticket = Ticket(
            price=listing.price, # El precio de reventa que pagó
            status=TicketStatus.ACTIVE,
            isValid=True,
            user_id=buyer.id, # <-- Nuevo dueño
            event_id=original_ticket.event_id,
            ticket_type_id=original_ticket.ticket_type_id,
            payment_id=payment_id, # El ID del NUEVO pago
            
            # Generar un nuevo QR es fundamental
            qrCode=f"qr_new_{uuid.uuid4()}" # Llama a tu función real de QR
        )
        self.db.add(new_ticket)
        
        # 5. Registrar la transferencia en el historial
        transfer_log = TicketTransfer(
            ticket_id=original_ticket.id, # ID del ticket original
            from_user_id=listing.seller_id,
            to_user_id=buyer.id,
            oldQR=original_ticket_qr,
            newQR=new_ticket.qrCode
        )
        self.db.add(transfer_log)
        
        # (Aquí también deberías crear la 'Transaction' para el vendedor y el comprador)
        
        try:
            self.db.commit()
            self.db.refresh(new_ticket)
            return new_ticket
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error atómico al transferir el ticket: {e}")