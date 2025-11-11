from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, func, exists  # Asegúrate de importar exists
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.schemas.ticket import MyTicketResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/my-tickets")
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene todos los tickets activos (o en reventa) que posee el usuario actual.
    """
    
    # --- INICIO DE LA CORRECCIÓN ---

    # 1. Obtener todos los tickets del usuario
    tickets = db.query(Ticket).filter(
        Ticket.user_id == current_user.id
    ).options(
        joinedload(Ticket.event),
        joinedload(Ticket.ticket_type)
    ).order_by(Ticket.purchaseDate.desc()).all()
    
    # 2. Para cada ticket, verificar si está listado en el marketplace
    response = []
    for ticket in tickets:
        # Buscar un listing ACTIVO para este ticket
        active_listing = db.query(MarketplaceListing).filter(
            MarketplaceListing.ticket_id == ticket.id,
            MarketplaceListing.status == ListingStatus.ACTIVE
        ).first()
        
        is_listed = active_listing is not None
        listing_id = str(active_listing.id) if active_listing else None
        
        print(f"🔍 Processing ticket {ticket.id}: is_listed={is_listed}, listing_id={listing_id}")
        
        # Construir el diccionario de respuesta
        ticket_dict = {
            'id': str(ticket.id),
            'price': float(ticket.price),
            'purchaseDate': ticket.purchaseDate.isoformat() if ticket.purchaseDate else None,
            'status': ticket.status.value,
            'isValid': ticket.isValid,
            'qrCode': ticket.qrCode if ticket.qrCode else None,  # Agregar el QR code
            'event': {
                'id': str(ticket.event.id),
                'title': ticket.event.title,
                'startDate': ticket.event.startDate.isoformat() if ticket.event.startDate else None,
                'venue': ticket.event.venue
            },
            'ticketType': {
                'id': str(ticket.ticket_type.id),
                'name': ticket.ticket_type.name
            },
            'isListed': is_listed,
            'listingId': listing_id
        }
        response.append(ticket_dict)

    print(f"📦 Returning {len(response)} tickets")
    if response:
        print(f"🔍 First ticket: {response[0]}")
    return response
    # --- FIN DE LA CORRECCIÓN ---