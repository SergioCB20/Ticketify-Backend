from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any, Dict, List
import uuid
import secrets
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_type import TicketType
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.purchase import Purchase, PurchaseStatus
from app.models.event import Event
from app.models.promotion import Promotion
from app.schemas.ticket import TicketCreateRequest

# Marketplace opcional (para evitar errores si el modelo no está)
try:
    from app.models.marketplace_listing import MarketplaceListing, ListingStatus
    MARKETPLACE_ENABLED = True
except Exception:
    MARKETPLACE_ENABLED = False


router = APIRouter(prefix="/tickets", tags=["Tickets"])


# =========================================================
# 🔹 Helper
# =========================================================
def _get_attr(obj, *names, default=None):
    """Lee atributos tolerante a snake/camel."""
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default


# =========================================================
# 🔹 Listar tickets del usuario
# =========================================================
@router.get("/my-tickets")
def get_my_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lista los tickets comprados por el usuario autenticado.
    Incluye datos del evento y si el ticket está listado en marketplace.
    """
    tickets: List[Ticket] = (
        db.query(Ticket)
        .filter(Ticket.user_id == current_user.id)
        .all()
    )

    items: List[Dict[str, Any]] = []
    for t in tickets:
        e = _get_attr(t, "event")
        tt = _get_attr(t, "ticket_type", "ticketType")

        # Marketplace (opcional)
        is_listed = False
        listing_id = None
        if MARKETPLACE_ENABLED:
            active_listing = (
                db.query(MarketplaceListing)
                .filter(
                    MarketplaceListing.ticket_id == t.id,
                    MarketplaceListing.status == ListingStatus.ACTIVE,
                )
                .first()
            )
            if active_listing:
                is_listed = True
                listing_id = str(active_listing.id)

        multimedia = _get_attr(e, "multimedia") or []
        cover = multimedia[0] if isinstance(multimedia, (list, tuple)) and multimedia else None

        status_val = _get_attr(t, "status")
        status_val = getattr(status_val, "value", status_val)

        items.append({
            "id": str(t.id),
            "price": _get_attr(t, "price"),
            "code": _get_attr(t, "qr_code", "qrCode", "code"),
            "purchase_date": _get_attr(t, "purchase_date", "purchaseDate"),
            "status": status_val,
            "is_valid": _get_attr(t, "isValid", "is_valid", default=True),
            "event": {
                "id": str(_get_attr(e, "id")) if e else None,
                "title": _get_attr(e, "title") if e else None,
                "start_date": _get_attr(e, "start_date", "startDate") if e else None,
                "venue": _get_attr(e, "venue") if e else None,
                "cover_image": cover,
            },
            "ticketType": {
                "id": str(_get_attr(tt, "id")) if tt else None,
                "name": _get_attr(tt, "name") if tt else None,
            },
            "isListed": is_listed,
            "listingId": listing_id,
        })

    total = len(items)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


# =========================================================
# 🔹 Detalle de un ticket
# =========================================================
@router.get("/my-tickets/{ticket_id}")
def get_my_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene el detalle de un ticket específico del usuario."""
    row = (
        db.query(Ticket, Event)
        .join(Event, Event.id == Ticket.event_id)
        .filter(Ticket.id == ticket_id, Ticket.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    t, e = row
    multimedia = _get_attr(e, "multimedia") or []
    cover = multimedia[0] if isinstance(multimedia, (list, tuple)) and multimedia else None

    status_val = _get_attr(t, "status")
    status_val = getattr(status_val, "value", status_val)

    return {
        "id": str(t.id),
        "price": _get_attr(t, "price"),
        "qr_code": _get_attr(t, "qr_code", "qrCode", "code"),
        "purchase_date": _get_attr(t, "purchase_date", "purchaseDate"),
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


# =========================================================
# 🔹 Crear ticket (checkout)
# =========================================================
@router.post("/", status_code=201)
def create_ticket(
    data: TicketCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea un ticket asociado al evento, tipo y promoción (si aplica).
    El precio ya viene con el descuento aplicado desde el frontend.
    """
    event_id = data.event_id
    ticket_type_id = data.ticket_type_id
    price = float(data.price)
    promo_code = data.promo_code

    print(f"[DEBUG] event_id={event_id}, ticket_type_id={ticket_type_id}, price={price}, promo_code={promo_code}")

    # 1️⃣ Validar tipo de ticket
    ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    if not ticket_type:
        raise HTTPException(status_code=404, detail="Tipo de ticket no encontrado")

    # 2️⃣ Validar stock
    if ticket_type.quantity_available is None or ticket_type.quantity_available <= 0:
        raise HTTPException(status_code=400, detail="Entradas agotadas")

    # 3️⃣ Validar precio
    if price <= 0:
        raise HTTPException(status_code=400, detail="El precio final no puede ser cero o negativo.")

    # 4️⃣ Registrar promoción
    applied_promo = None
    if promo_code:
        promo = (
            db.query(Promotion)
            .filter(Promotion.code == promo_code, Promotion.status == "ACTIVE")
            .first()
        )
        if promo:
            applied_promo = promo
            promo.current_uses = (promo.current_uses or 0) + 1
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
        subtotal=price,
        tax_amount=0,
        service_fee=0,
        discount_amount=0,
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
