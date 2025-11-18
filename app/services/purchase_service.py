from sqlalchemy.orm import Session
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import logging

from app.models.purchase import Purchase, PurchaseStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.event import Event
from app.models.user import User
from app.models.promotion import Promotion

logger = logging.getLogger(__name__)

class PurchaseService:

    @staticmethod
    def calculate_purchase_amount(
        ticket_selections: list,
        promotion: Promotion = None
    ) -> dict:
        """
        Calcula el monto total de la compra con descuentos aplicados.
        
        Args:
            ticket_selections: Lista de dict con ticketTypeId y quantity
            promotion: Promoción a aplicar (opcional)
            
        Returns:
            dict con subtotal, discount_amount, tax_amount, service_fee, total
        """
        subtotal = Decimal("0.00")
        total_quantity = 0
        
        for selection in ticket_selections:
            ticket_type = selection['ticket_type']
            quantity = selection['quantity']
            price = Decimal(str(ticket_type.price))
            
            subtotal += price * quantity
            total_quantity += quantity
        
        # Calcular descuento
        discount_amount = Decimal("0.00")
        if promotion:
            if promotion.promotion_type == "PERCENTAGE":
                discount_amount = (subtotal * Decimal(str(promotion.discount_value))) / Decimal("100")
            elif promotion.promotion_type == "FIXED_AMOUNT":
                discount_amount = Decimal(str(promotion.discount_value))
            elif promotion.promotion_type == "BUY_X_GET_Y":
                # Lógica de buy X get Y
                x_quantity = promotion.min_purchase_quantity or 1
                if total_quantity >= x_quantity:
                    # Calcular cuántos tickets gratis
                    free_tickets = total_quantity // x_quantity
                    # Precio promedio por ticket
                    avg_price = subtotal / total_quantity
                    discount_amount = avg_price * free_tickets
        
        # Asegurar que el descuento no sea mayor que el subtotal
        discount_amount = min(discount_amount, subtotal)
        
        # Calcular impuestos y tarifas (ajustar según necesites)
        tax_amount = Decimal("0.00")  # 0% de impuestos por ahora
        service_fee = Decimal("0.00")  # Sin tarifa de servicio por ahora
        
        total = subtotal - discount_amount + tax_amount + service_fee
        
        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "service_fee": service_fee,
            "total_amount": total,
            "quantity": total_quantity
        }

    @staticmethod
    def finalize_purchase_transaction(
        db: Session, 
        purchase: Purchase,
        payment_info: dict
    ) -> bool:
        """
        Finaliza una compra APROBADA por MercadoPago.
        Esta función es llamada por el Webhook.
        
        Args:
            db: Sesión de base de datos
            purchase: Objeto Purchase de la compra
            payment_info: Diccionario con datos del pago de MP
            
        Returns:
            bool: True si la compra se finalizó correctamente
        """
        
        try:
            # 1. Verificar que no esté ya procesada
            if purchase.status == PurchaseStatus.COMPLETED:
                logger.info(f"La compra {purchase.id} ya fue procesada.")
                return True

            if purchase.status not in [PurchaseStatus.PENDING, PurchaseStatus.PROCESSING]:
                raise Exception(f"La compra {purchase.id} no está en estado válido para procesar (estado: {purchase.status})")

            # Cambiar estado a procesando
            purchase.status = PurchaseStatus.PROCESSING
            db.flush()

            # 2. CREAR REGISTRO DE PAGO
            payment = Payment(
                amount=Decimal(str(payment_info["amount"])),
                paymentMethod=PaymentMethod.MERCADOPAGO,
                transactionId=str(payment_info["id"]),
                status=PaymentStatus.COMPLETED,
                paymentDate=datetime.now(timezone.utc),
                user_id=purchase.user_id
            )
            db.add(payment)
            db.flush()

            # 3. GENERAR LOS TICKETS CON QR
            # Obtener todos los ticket_types de esta compra
            tickets_created = []
            
            # Si la compra tiene ticket_type_id (compra simple de un tipo)
            if purchase.ticket_type_id:
                ticket_type = db.query(TicketType).filter(
                    TicketType.id == purchase.ticket_type_id
                ).first()
                
                if not ticket_type:
                    raise Exception(f"Tipo de ticket {purchase.ticket_type_id} no encontrado.")
                
                for i in range(purchase.quantity):
                    ticket = Ticket(
                        price=ticket_type.price,
                        status=TicketStatus.ACTIVE,
                        isValid=True,
                        user_id=purchase.user_id,
                        event_id=purchase.event_id,
                        ticket_type_id=ticket_type.id,
                        payment_id=payment.id,
                        purchase_id=purchase.id
                    )
                    db.add(ticket)
                    db.flush()
                    
                    # Generar QR
                    ticket.generate_qr()
                    tickets_created.append(ticket)
                
                # Actualizar disponibilidad
                ticket_type.quantity_available -= purchase.quantity
                ticket_type.sold_quantity += purchase.quantity
            else:
                # Compra múltiple de diferentes tipos
                # Los tickets ya deberían estar creados en Purchase.notes como JSON
                # O podemos obtenerlos de otra forma
                # Por ahora, vamos a asumir que se guardan en notes
                import json
                if purchase.notes:
                    ticket_selections = json.loads(purchase.notes)
                    for selection in ticket_selections:
                        ticket_type_id = selection['ticketTypeId']
                        quantity = selection['quantity']
                        
                        ticket_type = db.query(TicketType).filter(
                            TicketType.id == ticket_type_id
                        ).first()
                        
                        if not ticket_type:
                            logger.warning(f"Tipo de ticket {ticket_type_id} no encontrado.")
                            continue
                        
                        for i in range(quantity):
                            ticket = Ticket(
                                price=ticket_type.price,
                                status=TicketStatus.ACTIVE,
                                isValid=True,
                                user_id=purchase.user_id,
                                event_id=purchase.event_id,
                                ticket_type_id=ticket_type.id,
                                payment_id=payment.id,
                                purchase_id=purchase.id
                            )
                            db.add(ticket)
                            db.flush()
                            
                            # Generar QR
                            ticket.generate_qr()
                            tickets_created.append(ticket)
                        
                        # Actualizar disponibilidad
                        ticket_type.quantity_available -= quantity
                        ticket_type.sold_quantity += quantity
            
            # 4. ACTUALIZAR LA COMPRA
            purchase.status = PurchaseStatus.COMPLETED
            purchase.payment_id = payment.id
            purchase.payment_date = datetime.now(timezone.utc)
            purchase.confirmation_date = datetime.now(timezone.utc)
            purchase.payment_reference = str(payment_info["id"])
            
            # 5. COMMIT DE LA TRANSACCIÓN
            db.flush()
            
            logger.info(f"✅ Compra {purchase.id} finalizada exitosamente. {len(tickets_created)} tickets creados.")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error al finalizar compra {purchase.id}: {str(e)}")
            purchase.status = PurchaseStatus.FAILED
            db.flush()
            raise
    
    @staticmethod
    def get_user_purchases(
        db: Session,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10
    ) -> tuple:
        """
        Obtiene las compras de un usuario con paginación.
        
        Returns:
            tuple: (purchases, total_count)
        """
        query = db.query(Purchase).filter(
            Purchase.user_id == user_id
        ).order_by(Purchase.created_at.desc())
        
        total = query.count()
        offset = (page - 1) * page_size
        
        purchases = query.offset(offset).limit(page_size).all()
        
        return purchases, total
    
    @staticmethod
    def get_purchase_details(
        db: Session,
        purchase_id: uuid.UUID,
        user_id: uuid.UUID = None
    ) -> Purchase:
        """
        Obtiene el detalle de una compra.
        Si se proporciona user_id, valida que la compra pertenezca al usuario.
        """
        query = db.query(Purchase).filter(Purchase.id == purchase_id)
        
        if user_id:
            query = query.filter(Purchase.user_id == user_id)
        
        purchase = query.first()
        
        if not purchase:
            raise Exception("Compra no encontrada")
        
        return purchase
