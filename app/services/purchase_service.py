from sqlalchemy.orm import Session
from datetime import datetime, timezone
from decimal import Decimal
import uuid
import logging
from fastapi import HTTPException, status

from app.models.purchase import Purchase, PurchaseStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.event import Event
from app.models.user import User
from app.models.promotion import Promotion
from app.utils.email_service import email_service
# Si tienes qr_generator.py, impórtalo. Si no, comenta esta línea.
from app.utils.qr_generator import generate_ticket_qr_data, generate_qr_image

logger = logging.getLogger(__name__)

class PurchaseService:

    @staticmethod
    def calculate_purchase_amount(
        ticket_selections: list,
        promotion: Promotion = None
    ) -> dict:
        """
        Calcula el monto total de la compra con descuentos aplicados.
        """
        subtotal = Decimal("0.00")
        
        for selection in ticket_selections:
            ticket_type = selection['ticket_type']
            quantity = selection['quantity']
            price = Decimal(str(ticket_type.price))
            
            subtotal += price * quantity
        
        # Calcular descuento
        discount_amount = Decimal("0.00")
        if promotion:
            if promotion.promotion_type == "PERCENTAGE":
                discount_percent = Decimal(str(promotion.discount_value)) / 100
                discount_amount = subtotal * discount_percent
            elif promotion.promotion_type == "FIXED_AMOUNT":
                discount_amount = Decimal(str(promotion.discount_value))
        
        # Calcular impuestos y fees
        tax_rate = Decimal("0.00")
        service_fee_rate = Decimal("0.10") # 10% comisión
        
        service_fee = subtotal * service_fee_rate
        tax_amount = subtotal * tax_rate
        
        total = subtotal + service_fee + tax_amount - discount_amount
        if total < 0: total = Decimal("0.00")
        
        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "service_fee": service_fee,
            "total": total
        }

    @staticmethod
    def create_pending_purchase(
        db: Session,
        user_id: uuid.UUID,
        event_id: uuid.UUID,
        tickets_data: list, 
        promotion_code: str = None
    ) -> tuple[Purchase, list]:
        """
        Crea una compra en estado PENDING y valida el stock.
        """
        # 1. Obtener y validar el evento
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")

        # 2. Procesar tickets y validar stock
        mp_items = []
        ticket_selections = []
        
        for item in tickets_data:
            # Acceso híbrido (Soporta Pydantic y Dict)
            if isinstance(item, dict):
                t_id = item.get("ticketTypeId")
                qty = item.get("quantity")
            else:
                t_id = item.ticketTypeId
                qty = item.quantity

            ticket_type = db.query(TicketType).filter(
                TicketType.id == t_id, 
                TicketType.event_id == event.id
            ).first()
            
            if not ticket_type:
                raise HTTPException(status_code=404, detail=f"Tipo de ticket {t_id} no encontrado")
            
            # ✅ CORRECCIÓN: Calcular stock disponible manualmente
            available_stock = ticket_type.quantity_available - ticket_type.sold_quantity
            
            if available_stock < qty:
                raise HTTPException(
                    status_code=400, 
                    detail=f"No hay suficiente stock para {ticket_type.name}. Disponibles: {available_stock}"
                )

            ticket_selections.append({
                "ticket_type": ticket_type,
                "quantity": qty
            })
            
            mp_items.append({
                "id": str(ticket_type.id),
                "title": f"{event.title} - {ticket_type.name}",
                "quantity": qty,
                "unit_price": float(ticket_type.price),
                "currency_id": "PEN"
            })

        # 3. Validar Promoción
        promotion = None
        if promotion_code:
            promotion = db.query(Promotion).filter(
                Promotion.code == promotion_code,
                Promotion.event_id == event.id,
                Promotion.is_active == True
            ).first()

        # 4. Calcular montos
        amounts = PurchaseService.calculate_purchase_amount(ticket_selections, promotion)

        # --- CÁLCULO DEL UNIT_PRICE (Requerido por el modelo Purchase) ---
        total_qty = sum(t["quantity"] for t in ticket_selections)
        if total_qty > 0:
            avg_unit_price = amounts["subtotal"] / total_qty
        else:
            avg_unit_price = Decimal("0.00")
        # -----------------------------------------------------------------

        # 5. Crear la Compra
        new_purchase = Purchase(
            user_id=user_id,
            event_id=event_id,
            status=PurchaseStatus.PENDING,
            total_amount=amounts["total"],
            subtotal=amounts["subtotal"],
            service_fee=amounts["service_fee"],
            tax_amount=amounts["tax_amount"],
            discount_amount=amounts["discount_amount"],
            quantity=total_qty,
            unit_price=avg_unit_price, # ✅ Campo añadido
            buyer_email="", 
            promotion_id=promotion.id if promotion else None
        )
        
        db.add(new_purchase)
        db.commit()
        db.refresh(new_purchase)
        
        return new_purchase, mp_items

    @staticmethod
    def finalize_purchase_transaction(
        db: Session,
        purchase: Purchase,
        payment_info: dict
    ) -> Purchase:
        """
        Finaliza una compra exitosa: Genera tickets y actualiza stock.
        """
        try:
            logger.info(f"🔄 Iniciando finalización de compra {purchase.id}")
            
            # 1. Actualizar estado de compra
            purchase.status = PurchaseStatus.COMPLETED
            purchase.payment_date = datetime.now(timezone.utc)
            purchase.payment_reference = str(payment_info.get("id"))
            purchase.confirmation_date = datetime.now(timezone.utc)
            
            logger.info(f"✅ Purchase status updated to COMPLETED")
            
            # 2. Obtener el tipo de ticket
            # NOTA: Esto es simplificado. Idealmente deberías tener una tabla intermedia
            # purchase_items que contenga el detalle de qué ticket_types y cantidades se compraron.
            
            ticket_type_id = purchase.ticket_type_id
            
            # Si no hay ticket_type_id en purchase, buscar el primero del evento
            if not ticket_type_id:
                logger.warning(f"⚠️ Purchase {purchase.id} no tiene ticket_type_id, buscando fallback")
                first_tt = db.query(TicketType).filter(
                    TicketType.event_id == purchase.event_id,
                    TicketType.is_active == True
                ).first()
                
                if not first_tt:
                    raise Exception(f"No se encontró ningún tipo de ticket activo para el evento {purchase.event_id}")
                
                ticket_type_id = first_tt.id
                logger.info(f"✅ Usando ticket_type fallback: {ticket_type_id}")
            
            # 3. Verificar que el ticket_type existe
            ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
            if not ticket_type:
                raise Exception(f"Ticket type {ticket_type_id} no encontrado")
            
            logger.info(f"✅ Ticket type found: {ticket_type.name}")
            
            # 4. Crear registro de Payment si no existe
            if not purchase.payment_id:
                new_payment = Payment(
                    user_id=purchase.user_id,
                    amount=purchase.total_amount,
                    paymentMethod=PaymentMethod.MERCADOPAGO,
                    status=PaymentStatus.COMPLETED,
                    transactionId=str(payment_info.get("id")),
                    paymentDate=datetime.now(timezone.utc)
                )
                db.add(new_payment)
                db.flush()  # Para obtener el ID
                purchase.payment_id = new_payment.id
                logger.info(f"✅ Payment created: {new_payment.id}")
            
            # 5. Generar los tickets
            tickets_created = 0
            for i in range(purchase.quantity):
                try:
                    new_ticket = Ticket(
                        event_id=purchase.event_id,
                        user_id=purchase.user_id,
                        purchase_id=purchase.id,
                        status=TicketStatus.ACTIVE,
                        ticket_type_id=ticket_type_id,
                        price=ticket_type.price,
                        isValid=True,
                        payment_id=purchase.payment_id  # Campo requerido por el modelo
                    )
                    
                    # Generar QR (si tienes la función descomentada)
                    # try:
                    #     qr_content = f"TICKET-{new_ticket.id}"
                    #     new_ticket.qr_code = generate_qr_code(qr_content)
                    # except Exception as e:
                    #     logger.warning(f"No se pudo generar QR: {e}")
                   
                    qr_payload = generate_ticket_qr_data(str(new_ticket.id), str(purchase.event_id))
                    new_ticket.qrCode = generate_qr_image(qr_payload)

                    logger.info(f"🟢 QR generado (purchase) → {new_ticket.id}: {new_ticket.qrCode[:60]}")

                    db.add(new_ticket)
                    db.flush()
                    new_ticket.generate_qr()
                    
                    tickets_created += 1
                    logger.info(f"✅ Ticket {i+1}/{purchase.quantity} created with QR")
                    
                except Exception as ticket_error:
                    logger.error(f"❌ Error creating ticket {i+1}: {str(ticket_error)}")
                    raise Exception(f"Error al crear ticket {i+1}: {str(ticket_error)}")
            
            # 6. Actualizar stock vendido
            try:
                ticket_type.sold_quantity += purchase.quantity
                logger.info(f"✅ Stock updated: {ticket_type.name} sold_quantity = {ticket_type.sold_quantity}")
            except Exception as stock_error:
                logger.error(f"❌ Error updating stock: {str(stock_error)}")
                raise Exception(f"Error al actualizar stock: {str(stock_error)}")
            
            # 7. Flush para guardar cambios
            db.flush()
            logger.info(f"✅ Compra {purchase.id} finalizada exitosamente. {tickets_created} tickets creados")
            # Cargar evento y usuario (para evitar lazy loading)
            event = db.query(Event).filter(Event.id == purchase.event_id).first()
            user = db.query(User).filter(User.id == purchase.user_id).first()

            if not event:
                raise Exception("Evento no encontrado durante finalización")
            if not user:
                raise Exception("Usuario no encontrado durante finalización")
            try:
                # Preparar datos de tickets
                ticket_data = [
                    {
                        "id": str(t.id),
                        "qrCode": t.qrCode,
                        "price": float(t.price)
                    }
                    for t in purchase.tickets
                ]

                email_service.send_ticket_email(
                    to_email=purchase.buyer_email,
                    first_name=user.firstName if user.firstName else "Cliente",
                    event_title=event.title,
                    event_date=event.startDate.strftime("%d/%m/%Y %H:%M"),
                    event_venue=event.venue,
                    tickets=ticket_data
                )

                logger.info(f"📧 Email con tickets enviado correctamente a {purchase.buyer_email}")

            except Exception as email_error:
                logger.error(f"❌ Error enviando email con tickets: {str(email_error)}")

            return purchase

        except Exception as e:
            logger.error(f"❌ Error al finalizar compra {purchase.id}: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Error details: {repr(e)}")
            
            # Marcar compra como fallida
            try:
                purchase.status = PurchaseStatus.FAILED
                db.flush()
            except Exception as status_error:
                logger.error(f"❌ No se pudo actualizar status a FAILED: {str(status_error)}")
            
            raise Exception(f"Error al finalizar compra: {str(e)}")

    @staticmethod
    def get_user_purchases(
        db: Session,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 10
    ) -> tuple:
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
        query = db.query(Purchase).filter(Purchase.id == purchase_id)
        if user_id:
            query = query.filter(Purchase.user_id == user_id)
        
        purchase = query.first()
        if not purchase:
            raise HTTPException(status_code=404, detail="Compra no encontrada")
            
        return purchase
