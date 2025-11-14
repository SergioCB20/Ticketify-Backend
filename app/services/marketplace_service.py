from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from uuid import UUID
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_transfer import TicketTransfer
from app.models.user import User
from fastapi import HTTPException, status


class MarketplaceService:

    def __init__(self, db: Session):
        self.db = db

    def buy_ticket(self, db: Session, listing_id: UUID, buyer: User) -> MarketplaceListing:
        """
        Lógica para comprar un ticket del marketplace.
        """
        # 1. Encontrar el listado
        listing = db.query(MarketplaceListing).filter(MarketplaceListing.id == listing_id).first()
        if not listing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

        # 2. Verificar que el listado esté disponible
        if listing.status != ListingStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket is not available for purchase")

        # 3. Encontrar el ticket asociado
        ticket = db.query(Ticket).filter(Ticket.id == listing.ticket_id).first()
        if not ticket:
            # Esto es un error de integridad de datos, pero lo manejamos
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated ticket not found")

        # 4. Verificar que el comprador no sea el mismo vendedor
        if ticket.owner_id == buyer.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot buy your own ticket")

        # 5. Procesar la "compra" (Transferir propiedad y actualizar listado)
        try:
            # a. Transferir la propiedad del ticket
            ticket.owner_id = buyer.id
            
            # b. Marcar el listado como "vendido"
            listing.status = "sold"

            # (Aquí iría la lógica de pago, creación de transacción, etc.)
            
            db.add(ticket)
            db.add(listing)
            db.commit()
            db.refresh(listing)
            
            return listing
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred during the purchase: {str(e)}")


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
            purchase_id=original_ticket.purchase_id
        )
        self.db.add(new_ticket)
        self.db.flush()  # Asegurar que el ticket tenga ID antes de generar QR
        
        # Generar QR visual para el nuevo ticket
        new_ticket.generate_qr()
        print(f"✅ Nuevo QR generado para ticket {new_ticket.id}: {new_ticket.qrCode[:50]}...")  # Log temporal
        
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