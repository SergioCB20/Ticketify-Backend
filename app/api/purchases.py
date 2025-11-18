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
    TicketResponse,
    CreatePreferenceRequest,
    CreatePreferenceRespons
)
from app.services.payment_service import PaymentService


router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post("/process", response_model=PurchaseResponse)
async def process_purchase(
    request: ProcessPaymentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_attendee_user)
    payment_service: PaymentService = Depends(PaymentService)
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
    total_amount = Decimal(str(ticket_type.price)) * request.quantity
    purchase = Purchase(
        total_amount=total_amount,
        subtotal=total_amount,
        tax_amount=Decimal("0.00"),
        service_fee=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        quantity=request.quantity,
        unit_price=ticket_type.price,
        status=PurchaseStatus.PENDING, # Estado PENDIENTE
        payment_method=PaymentMethod.MERCADOPAGO, # O el método que corresponda
        buyer_email=current_user.email,
        purchase_date=datetime.now(timezone.utc),
        user_id=current_user.id,
        event_id=event.id,
        ticket_type_id=ticket_type.id,
        payment_id=None # Aún no hay pago
    )
    db.add(purchase)
    db.flush()
    try:
        # 5. PREPARAR ITEMS PARA MERCADOPAGO
        items_list = [{
            "title": f"{ticket_type.name} - {event.name}",
            "quantity": request.quantity,
            "unit_price": float(ticket_type.price),
            "currency_id": "PEN" # Ajusta tu moneda
        }]

        # 6. CREAR PREFERENCIA DE PAGO
        preference = payment_service.create_event_preference(
            purchase=purchase,
            items=items_list,
            buyer_email=current_user.email
        )
        
        # 7. Guardar el ID de preferencia en la compra
        purchase.mercadopago_preference_id = preference["id"]
        
        db.commit() # Confirmamos la creación de la compra y el pref_id
        db.refresh(purchase)
        
        # 8. DEVOLVER EL INIT_POINT AL FRONTEND
        return CreatePreferenceResponse(
            purchaseId=purchase.id,
            init_point=preference["init_point"]
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la preferencia de pago: {str(e)}"
        )