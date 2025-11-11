# app/api/tickets.py
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from sqlalchemy.orm import Session
from uuid import UUID
import uuid
from typing import Any, Dict, List
from app.core.dependencies import get_db, get_current_user
import secrets
from datetime import datetime
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.purchase import Purchase, PurchaseStatus
from app.models import Event, Promotion
from app.schemas.ticket import TicketCreateRequest

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _get_attr(obj, *names, default=None):
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default

@router.get("/my-tickets")
def list_my_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    q = (
        db.query(Ticket, Event)
        .join(Event, Event.id == Ticket.event_id)
        .filter(Ticket.user_id == current_user.id)
    )

    total = q.count()
    rows = (
        q.order_by(
            # intenta por purchase_date, si no existe usa created_at, y si no, id
            _get_attr(Ticket, "purchase_date", "purchaseDate", "created_at", "createdAt", "id")
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items: List[Dict[str, Any]] = []
    for t, e in rows:
        purchase_date = _get_attr(t, "purchase_date", "purchaseDate")
        qr_code = _get_attr(t, "qr_code", "qrCode", "code")
        status_val = _get_attr(t, "status")
        status_val = getattr(status_val, "value", status_val)  # enum o str

        multimedia = _get_attr(e, "multimedia") or []
        cover = None
        try:
            cover = multimedia[0] if isinstance(multimedia, (list, tuple)) and multimedia else None
        except Exception:
            cover = None

        item = {
            "id": str(t.id),
            "code": qr_code,
            "status": status_val,
            "purchase_date": purchase_date,
            "event": {
                "id": str(e.id),
                "title": e.title,
                "start_date": _get_attr(e, "start_date", "startDate"),
                "venue": e.venue,
                "cover_image": cover,
            },
        }
        items.append(item)

    return {"items": items, "total": total, "page": page, "page_size": page_size}

@router.get("/my-tickets/{ticket_id}")
def get_my_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    row = (
        db.query(Ticket, Event)
        .join(Event, Event.id == Ticket.event_id)
        .filter(Ticket.id == ticket_id, Ticket.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    t, e = row
    purchase_date = _get_attr(t, "purchase_date", "purchaseDate")
    qr_code = _get_attr(t, "qr_code", "qrCode", "code")
    status_val = _get_attr(t, "status")
    status_val = getattr(status_val, "value", status_val)

    multimedia = _get_attr(e, "multimedia") or []
    cover = None
    try:
        cover = multimedia[0] if isinstance(multimedia, (list, tuple)) and multimedia else None
    except Exception:
        cover = None

    return {
        "id": str(t.id),
        "price": _get_attr(t, "price"),
        "qr_code": qr_code,                    # <-- úsalo en el front para generar el QR
        "purchase_date": purchase_date,
        "status": status_val,
        "event": {
            "id": str(e.id),
            "title": e.title,
            "start_date": _get_attr(e, "start_date", "startDate"),
            "end_date": _get_attr(e, "end_date", "endDate"),
            "venue": e.venue,
            "multimedia": multimedia,
            "cover_image": cover,
        },
    }

@router.post("/", status_code=201)
def create_ticket(
    data: TicketCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    event_id = data.event_id
    ticket_type_id = data.ticket_type_id
    price = float(data.price)  # 🟢 ya viene con el descuento aplicado
    promo_code = data.promo_code

    print(f"[DEBUG] event_id={event_id}, ticket_type_id={ticket_type_id}, price={price}, promo_code={promo_code}")

    # 1️⃣ Validar tipo de ticket
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Tipo de ticket no encontrado")

    # 2️⃣ Validar stock
    if ticket_type.quantity_available is None or ticket_type.quantity_available <= 0:
        raise HTTPException(status_code=400, detail="Entradas agotadas")

    # 3️⃣ Validar que el precio no sea cero o negativo
    if price <= 0:
        raise HTTPException(status_code=400, detail="El precio final del ticket no puede ser cero o negativo.")

    # 4️⃣ Registrar promoción (sin recalcular)
    applied_promo = None
    if promo_code:
        promo = (
            db.query(Promotion)
            .filter(Promotion.code == promo_code, Promotion.status == "ACTIVE")
            .first()
        )
        if promo:
            applied_promo = promo
            promo.max_uses_per_user = (promo.max_uses_per_user or 0) + 1
            db.add(promo)
        else:
            print(f"[WARN] Código de promoción {promo_code} no encontrado o inactivo — ignorado.")

    # 5️⃣ Crear Payment
    payment = Payment(
        amount=price,
        paymentMethod=PaymentMethod.CREDIT_CARD,
        status=PaymentStatus.COMPLETED,
        user_id=current_user.id,
    )
    db.add(payment)
    db.flush()

    # 6️⃣ Crear Purchase
    purchase = Purchase(
        user_id=current_user.id,
        event_id=event_id,
        ticket_type_id=ticket_type_id,
        total_amount=price,
        subtotal=price,  # ya viene final
        tax_amount=0,
        service_fee=0,
        discount_amount=0,  # el descuento ya fue aplicado en el front
        quantity=1,
        unit_price=price,
        status=PurchaseStatus.COMPLETED,
        payment_method=PaymentMethod.CREDIT_CARD,
        buyer_email=current_user.email,
        promotion_id=applied_promo.id if applied_promo else None,
    )
    db.add(purchase)
    db.flush()

    # 7️⃣ Crear Ticket
    ticket = Ticket(
        price=price,
        user_id=current_user.id,
        event_id=event_id,
        ticket_type_id=ticket_type_id,
        payment_id=payment.id,
        purchase_id=purchase.id,
    )
    ticket.generate_qr()
    db.add(ticket)

    # 8️⃣ Actualizar stock
    ticket_type.sold_quantity = (ticket_type.sold_quantity or 0) + 1
    ticket_type.quantity_available = max((ticket_type.quantity_available or 0) - 1, 0)
    db.add(ticket_type)

    # 9️⃣ Guardar todo
    db.commit()
    db.refresh(ticket)

    print(f"[DEBUG] ✅ Ticket creado: ID={ticket.id}, Precio final={price}")

    return {
        "message": "✅ Ticket creado exitosamente",
        "ticket": ticket.to_dict(),
    }
