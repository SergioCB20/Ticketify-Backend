from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, func, exists
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.schemas.ticket import MyTicketResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/my-tickets", response_model=List[MyTicketResponse])
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene todos los tickets activos (o en reventa) que posee el usuario actual.
    """
    
    # Subconsulta para ver si un ticket ya está listado y ACTIVO
    is_listed_subquery = (
        select(func.count(MarketplaceListing.id))
        .where(
            MarketplaceListing.ticket_id == Ticket.id,
            MarketplaceListing.status == ListingStatus.ACTIVE
        )
        .correlate(Ticket)
        .as_scalar()
    )

    tickets = db.scalars(
        select(Ticket)
        .options(
            joinedload(Ticket.event),
            joinedload(Ticket.ticket_type)
        )
        .where(
            Ticket.user_id == current_user.id,
            # Solo mostrar tickets que se pueden vender (ACTIVOS)
            # o que ya están en reventa (TRANSFERRED)
            Ticket.status.in_([TicketStatus.ACTIVE, TicketStatus.TRANSFERRED])
        )
        .order_by(Ticket.purchaseDate.desc())
        .add_columns(is_listed_subquery > 0) # Añade el booleano 'is_listed'
    ).all()

    # Mapear los resultados al schema
    response = []
    for ticket, is_listed in tickets:
        ticket.is_listed = is_listed # Asignar el valor al objeto
        response.append(ticket)

    return response