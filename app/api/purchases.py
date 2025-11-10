"""
API Endpoint para compras directas de tickets (no marketplace)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from datetime import timezone

from app.core.database import get_db
from app.core.dependencies import get_attendee_user
from app.models.user import User
from app.models.event import Event
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.purchase import Purchase, PurchaseStatus
from app.schemas.purchase import (
    ProcessPaymentRequest,
    PurchaseResponse,
    TicketResponse
)

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post("/process", response_model=PurchaseResponse)
async def process_purchase(
    request: ProcessPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_attendee_user)
):
    """
    Procesa la compra directa de tickets de un evento.
    Simula el procesamiento del pago y genera los tickets con QR.
    """
    
    # 1. VALIDAR EVENTO
    event = db.query(Event).filter(Event.id == request.purchase.eventId).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento no existe"
        )
    
    # Verificar que el evento no haya pasado
    if event.startDate < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden comprar tickets para eventos pasados"
        )
    
    # 2. VALIDAR TIPO DE TICKET
    ticket_type = db.query(TicketType).filter(
        TicketType.id == request.purchase.ticketTypeId,
        TicketType.event_id == event.id
    ).first()
    
    if not ticket_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El tipo de ticket no existe para este evento"
        )
    
    # Verificar disponibilidad
    if ticket_type.available < request.purchase.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Solo quedan {ticket_type.available} tickets disponibles"
        )
    
    # 3. CALCULAR MONTO TOTAL
    total_amount = float(ticket_type.price) * request.purchase.quantity
    
    # 4. SIMULAR PROCESAMIENTO DE PAGO (Datos ficticios)
    # En producción, aquí se llamaría a MercadoPago u otro gateway
    payment_successful, payment_message = _simulate_payment_processing(
        card_number=request.payment.cardNumber,
        amount=total_amount
    )
    
    if not payment_successful:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=payment_message
        )
    
    # 5. CREAR REGISTRO DE PAGO
    payment = Payment(
        amount=Decimal(str(total_amount)),
        paymentMethod=PaymentMethod.CREDIT_CARD,
        transactionId=f"txn_sim_{uuid4()}",  # ID simulado
        status=PaymentStatus.COMPLETED,
        paymentDate=datetime.utcnow(),
        user_id=current_user.id
    )
    db.add(payment)
    db.flush()  # Obtener el payment.id
    
    # 6. CREAR REGISTRO DE COMPRA
    purchase = Purchase(
    total_amount=Decimal(str(total_amount)),
    subtotal=Decimal(str(total_amount)),  # ✅ Igualamos subtotal al total
    tax_amount=Decimal("0.00"),
    service_fee=Decimal("0.00"),
    discount_amount=Decimal("0.00"),
    quantity=request.purchase.quantity,
    unit_price=ticket_type.price,
    status=PurchaseStatus.COMPLETED,
    payment_method=PaymentMethod.CREDIT_CARD,
    buyer_email=current_user.email,
    purchase_date=datetime.now(timezone.utc),
    user_id=current_user.id,
    event_id=event.id,
    ticket_type_id=ticket_type.id,
    payment_id=payment.id
)

    db.add(purchase)
    db.flush()  # Obtener el purchase.id
    
    # 7. GENERAR LOS TICKETS CON QR
    tickets_created = []
    
    for i in range(request.purchase.quantity):
        ticket = Ticket(
            price=ticket_type.price,
            status=TicketStatus.ACTIVE,
            isValid=True,
            user_id=current_user.id,
            event_id=event.id,
            ticket_type_id=ticket_type.id,
            payment_id=payment.id,
            purchase_id=purchase.id
        )
        db.add(ticket)
        db.flush()  # Asegurar que el ticket tenga ID
        
        # GENERAR QR VISUAL (esta es la parte clave de la Tarea 2)
        ticket.generate_qr()
        
        tickets_created.append(ticket)
    
    # 8. ACTUALIZAR DISPONIBILIDAD
    ticket_type.quantity_available -= request.purchase.quantity
    ticket_type.sold_quantity += request.purchase.quantity

    
    # 9. COMMIT DE TODA LA TRANSACCIÓN
    try:
        db.commit()
        
        # Refrescar objetos
        for ticket in tickets_created:
            db.refresh(ticket)
        db.refresh(payment)
        db.refresh(purchase)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la compra: {str(e)}"
        )
    
    # 10. CONSTRUIR RESPUESTA
    return PurchaseResponse(
        success=True,
        message=f"¡Compra exitosa! Se generaron {len(tickets_created)} ticket(s).",
        purchaseId=purchase.id,
        paymentId=payment.id,
        tickets=[
            TicketResponse(
                id=ticket.id,
                eventId=ticket.event_id,
                ticketTypeId=ticket.ticket_type_id,
                price=float(ticket.price),
                qrCode=ticket.qrCode,
                status=ticket.status.value,
                purchaseDate=ticket.purchaseDate.isoformat()
            )
            for ticket in tickets_created
        ],
        totalAmount=total_amount
    )


def _simulate_payment_processing(card_number: str, amount: float) -> tuple[bool, str]:
    """
    Simula el procesamiento de un pago.
    """
    last_digits = card_number[-4:]
    
    if last_digits == "0000":
        return (False, "Tarjeta rechazada por el banco emisor.")
    elif last_digits == "1111":
        return (False, "Fondos insuficientes.")
    else:
        return (True, "Pago aprobado.")

