from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from typing import Any, Dict, List

from app.core.dependencies import get_db, get_current_user  # usamos el mismo dep que ya te funciona
from app.models.user import User
from app.models.ticket import Ticket
from app.models.event import Event

# Marketplace (puede no existir en algunas ramas)
try:
    from app.models.marketplace_listing import MarketplaceListing, ListingStatus
    MARKETPLACE_ENABLED = True
except Exception:
    MARKETPLACE_ENABLED = False

router = APIRouter(prefix="/tickets", tags=["tickets"])


def _get_attr(obj, *names, default=None):
    """Lee atributo tolerante a snake/camel: purchase_date vs purchaseDate, etc."""
    for n in names:
        if hasattr(obj, n):
            return getattr(obj, n)
    return default


@router.get("/my-tickets")
def get_my_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Versión unificada: usa la lógica del 'main' (tickets del usuario + flag de marketplace),
    pero devuelve el shape que ya consume tu frontend: { items, total, page, page_size }.
    """
    # Trae los tickets del usuario con event y ticket_type (como en main)
    tickets: List[Ticket] = (
        db.query(Ticket)
        .filter(Ticket.user_id == current_user.id)
        .all()
    )

    items: List[Dict[str, Any]] = []
    for t in tickets:
        e = _get_attr(t, "event")
        tt = _get_attr(t, "ticket_type", "ticketType")

        # ¿Está listado en marketplace? (solo si el modelo existe)
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
        status_val = getattr(status_val, "value", status_val)  # enum o str

        item = {
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
        }
        items.append(item)

    total = len(items)
    # Mantiene el contrato { items, total, page, page_size } que ya usa tu front
    # (si quieres paginar de verdad, aplica slicing aquí)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/my-tickets/{ticket_id}")
def get_my_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Detalle de un ticket del usuario (mantiene tu endpoint original).
    """
    row = (
        db.query(Ticket, Event)
        .join(Event, Event.id == Ticket.event_id)
        .filter(Ticket.id == ticket_id, Ticket.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    t, e = row
    multimedia = _get_attr(e, "multimedia") or []
    cover = None
    try:
        cover = multimedia[0] if isinstance(multimedia, (list, tuple)) and multimedia else None
    except Exception:
        cover = None

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
