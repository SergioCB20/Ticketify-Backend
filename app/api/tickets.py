# app/api/tickets.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any, Dict, List
from app.core.dependencies import get_db, get_current_user

from app.models.ticket import Ticket
from app.models.event import Event

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