from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid
from uuid import UUID
from decimal import Decimal
import logging
from fastapi import HTTPException, status

from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_transfer import TicketTransfer
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.user import User
#nuevo para correos
from app.utils.email_service import email_service
from app.utils.qr_generator import generate_qr_image, generate_ticket_qr_data



logger = logging.getLogger(__name__)


class MarketplaceService:

    def __init__(self, db: Session):
        self.db = db

    def create_marketplace_payment_and_transfer(
        self,
        listing: MarketplaceListing,
        buyer: User,
        payment_info: dict,
        platform_fee: Decimal = None
    ) -> Ticket:
        """
        Procesa el pago del marketplace y transfiere el ticket al comprador.
        Similar a finalize_purchase_transaction pero para marketplace.
        
        Args:
            listing: El listing del marketplace
            buyer: Usuario comprador
            payment_info: Información del pago de MercadoPago
            
        Returns:
            Ticket: El nuevo ticket creado para el comprador
        """
        try:
            logger.info(f"🔄 Iniciando transferencia de marketplace para listing {listing.id}")
            
            # Calcular comisión si no se proveyó
            if platform_fee is None:
                platform_fee = Decimal(str(listing.price)) * Decimal("0.05")  # 5% de comisión
            
            logger.info(f"💰 Precio total: S/ {listing.price}")
            logger.info(f"💸 Comisión plataforma (5%): S/ {platform_fee}")
            logger.info(f"👤 Pago al vendedor: S/ {listing.price - platform_fee}")
            
            # 1. Crear el registro de Payment
            new_payment = Payment(
                user_id=buyer.id,
                amount=listing.price,
                paymentMethod=PaymentMethod.MERCADOPAGO,
                status=PaymentStatus.COMPLETED,
                transactionId=str(payment_info.get("id")),
                paymentDate=datetime.now(timezone.utc)
            )
            self.db.add(new_payment)
            self.db.flush()  # Para obtener el ID

            logger.info(f"✅ Payment created: {new_payment.id}")
            
            # 2. Obtener el ticket original
            original_ticket = listing.ticket
            if not original_ticket:
                raise Exception("No se encontró el ticket original asociado al listado.")
            
            # Guardar el QR original antes de invalidarlo
            original_ticket_qr = original_ticket.qrCode or ""
            
            # 3. Invalidar el ticket original (del vendedor)
            original_ticket.status = TicketStatus.TRANSFERRED
            original_ticket.isValid = False
            self.db.add(original_ticket)
            
            logger.info(f"✅ Ticket original {original_ticket.id} marcado como TRANSFERRED")
            
            # 4. Crear el NUEVO ticket para el comprador (exactamente como en events)
            new_ticket = Ticket(
                price=listing.price,  # El precio de reventa que pagó
                status=TicketStatus.ACTIVE,
                isValid=True,
                user_id=buyer.id,  # <-- Nuevo dueño
                event_id=original_ticket.event_id,
                ticket_type_id=original_ticket.ticket_type_id,
                payment_id=new_payment.id,  # El ID del NUEVO pago
                purchase_id=original_ticket.purchase_id  # Mantener referencia a la compra original
            )
            self.db.add(new_ticket)
            self.db.flush()  # Asegurar que el ticket tenga ID antes de generar QR
            
            # Generar QR para el nuevo ticket
            new_ticket.generate_qr()

            # 🔍 DEBUG REAL: Mostrar primeras letras del QR
            try:
                logger.info(f"🟢 QR generado para ticket {new_ticket.id}: {new_ticket.qrCode[:60]}...")
            except Exception:
                logger.warning(f"⚠ QR no tiene datos en new_ticket.qrCode justo después de generate_qr()")
            
            # 5. Actualizar el listing como VENDIDO
            listing.status = ListingStatus.SOLD
            listing.buyer_id = buyer.id
            listing.sold_at = datetime.now(timezone.utc)
            self.db.add(listing)
            
            logger.info(f"✅ Listing {listing.id} marcado como SOLD")
            
            # 6. Registrar la transferencia en el historial
            transfer_log = TicketTransfer(
                ticket_id=original_ticket.id,  # ID del ticket original
                from_user_id=listing.seller_id,
                to_user_id=buyer.id,
                oldQR=original_ticket_qr,
                newQR=new_ticket.qrCode
            )
            self.db.add(transfer_log)
            
            logger.info(f"✅ Transferencia registrada en TicketTransfer")
            
            # 7. Commit de todas las operaciones
            self.db.commit()
            self.db.refresh(new_ticket)

            # -------------------------------------------
            # 8. Enviar correos al comprador y vendedor
            # -------------------------------------------

            buyer = buyer
            seller = listing.seller
            event = original_ticket.event

            # 1. Generar el contenido del QR del ticket
            qr_payload = generate_ticket_qr_data(
                ticket_id=str(new_ticket.id),
                event_id=str(event.id)
            )

            # 2. Generar imagen QR en base64
            from app.utils.imgbb_upload import upload_qr_to_imgbb

            # genera el QR EN BASE64 como ya lo haces
            qr_image_base64 = generate_qr_image(qr_payload)

            # súbelo a imgbb
            qr_url = upload_qr_to_imgbb(qr_image_base64)

            # fallback si falla (caso raro)
            if not qr_url:
                qr_url = qr_image_base64

            
            # 3. Crear HTML del correo del comprador
            buyer_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8" />
            <title>Tu Ticket - Ticketify</title>
            </head>
            <body style="font-family: Arial; padding: 20px;">

            <h2 style="color: #7c3aed;">🎫 Tu entrada para: {event.title}</h2>

            <p>Hola {buyer.firstName},</p>

            <p>Tu compra ha sido confirmada. Aquí está tu ticket para el evento:</p>

            <div style="margin: 20px 0;">
            <img src="{qr_url}" alt="QR del ticket" style="width: 250px;" />
            </div>

            <p><strong>Evento:</strong> {event.title}</p>
            <p><strong>Fecha:</strong> {event.startDate}</p>
            <p><strong>Precio:</strong> S/ {listing.price}</p>
            <p><strong>ID del Ticket:</strong> {new_ticket.id}</p>

            <br>
            <p>¡Gracias por usar <strong>Ticketify</strong>!</p>

            </body>
            </html>
            """


            # 4. Enviar email al comprador
            email_service.send_email(
                to_email=buyer.email,
                subject=f"Tu entrada para {event.title}",
                html_content=buyer_html,
                text_content="Tu ticket está listo."
            )

            # 5. Crear HTML del correo del vendedor
            seller_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8" />
            <title>Ticket Vendido - Ticketify</title>
            </head>
            <body style="font-family: Arial; padding: 20px;">

            <h2 style="color: #10b981;">🎉 ¡Tu ticket ha sido vendido!</h2>

            <p>Hola {seller.firstName},</p>

            <p>Te informamos que tu ticket para <strong>{event.title}</strong> ha sido vendido.</p>

            <p><strong>Comprador:</strong> {buyer.firstName}</p>
            <p><strong>Precio de venta:</strong> S/ {listing.price}</p>

            <br>
            <p>¡Gracias por usar <strong>Ticketify</strong> para vender tus entradas!</p>

            </body>
            </html>
            """


            # 6. Enviar email al vendedor
            email_service.send_email(
                to_email=seller.email,
                subject="Tu ticket ha sido vendido",
                html_content=seller_html,
                text_content="Tu ticket ha sido vendido."
            )





            
            logger.info(f"✅ Transferencia de marketplace completada exitosamente")
            logger.info(f"💰 IMPORTANTE: El pago está en la cuenta de la plataforma")
            logger.info(f"💸 Monto del vendedor: S/ {listing.price - platform_fee} (después de comisión 5%)")
            logger.info(f"📋 TODO: Procesar transferencia manual al vendedor {listing.seller.email}")
            logger.info(f"👤 Vendedor ID: {listing.seller_id}, Buyer ID: {buyer.id}")
            
            return new_ticket
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error en transferencia de marketplace: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            raise Exception(f"Error al procesar la compra del marketplace: {str(e)}")

    def buy_ticket(self, db: Session, listing_id: UUID, buyer: User) -> MarketplaceListing:
        """
        Lógica para comprar un ticket del marketplace.
        DEPRECATED: Usar create_marketplace_payment_and_transfer en su lugar.
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
        payment_id: UUID
    ) -> Ticket:
        """
        DEPRECATED: Usar create_marketplace_payment_and_transfer en su lugar.
        Esta función está mantenida solo para compatibilidad con código existente.
        """
        logger.warning("⚠️ Usando función deprecated transfer_ticket_on_purchase")
        
        # Redirigir a la nueva implementación
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise Exception("Payment no encontrado")
        
        payment_info = {
            "id": payment.transactionId,
            "amount": float(payment.amount),
            "status": payment.status.value
        }
        
        return self.create_marketplace_payment_and_transfer(listing, buyer, payment_info)
