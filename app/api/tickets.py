from fastapi import APIRouter, Depends, HTTPException, status, Query # 👈 Asegúrate de importar Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, exists
from typing import List, Any, Dict # 👈 Añade Any y Dict

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
# (No necesitas app.schemas.ticket.MyTicketResponse para esta respuesta)

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/my-tickets")
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1), # 👈 RE-INTRODUCIR PAGINACIÓN
    page_size: int = Query(20, ge=1, le=100) # 👈 RE-INTRODUCIR PAGINACIÓN
):
    """
    Obtiene todos los tickets (paginados) que posee el usuario actual,
    indicando si están activamente listados en el marketplace.
    """
    
    # --- INICIO DE LA CORRECCIÓN (v2 - Eficiente y Paginada) ---

    # 1. Consulta base: Unir Ticket con un listing ACTIVO (si existe)
    # Usamos outerjoin para asegurar que obtenemos tickets INCLUSO SI NO tienen listing
    query = db.query(Ticket, MarketplaceListing).outerjoin(
        MarketplaceListing,
        (MarketplaceListing.ticket_id == Ticket.id) &
        (MarketplaceListing.status == ListingStatus.ACTIVE)
    ).filter(
        Ticket.user_id == current_user.id
    ).options(
        # Cargar relaciones del Ticket para evitar más queries
        joinedload(Ticket.event),
        joinedload(Ticket.ticket_type)
    )

    # 2. Contar el total de tickets del usuario ANTES de paginar
    # (Necesitamos una subquery para contar solo los tickets del usuario)
    total_query = db.query(func.count(Ticket.id)).filter(Ticket.user_id == current_user.id)
    total = total_query.scalar() or 0
    
    # 3. Aplicar paginación y orden
    offset = (page - 1) * page_size
    results = query.order_by(
        Ticket.purchaseDate.desc() # Ordenar por fecha de compra
    ).offset(
        offset
    ).limit(
        page_size
    ).all()
    
    # 4. Procesar los resultados (que son tuplas de (Ticket, MarketplaceListing | None))
    items: List[Dict[str, Any]] = []
    for (ticket, active_listing) in results:
        
        is_listed = active_listing is not None
        listing_id = str(active_listing.id) if active_listing else None
        
        # Obtener portada (similar a la lógica anterior)
        cover = ticket.event.photo
       

        # Construir el diccionario de respuesta
        ticket_dict = {
            'id': str(ticket.id),
            'price': float(ticket.price),
            'purchaseDate': ticket.purchaseDate.isoformat() if ticket.purchaseDate else None,
            'status': ticket.status.value,
            'isValid': ticket.isValid,
            'qrCode': ticket.qrCode if ticket.qrCode else None,
            'code': ticket.qrCode if ticket.qrCode else None, # Añado 'code' por si el frontend lo usa
            'event': {
                'id': str(ticket.event.id),
                'title': ticket.event.title,
                'startDate': ticket.event.startDate.isoformat() if ticket.event.startDate else None,
                'start_date': ticket.event.startDate.isoformat() if ticket.event.startDate else None,
                'venue': ticket.event.venue,
                'cover_image': cover,
            },
            'ticketType': {
                'id': str(ticket.ticket_type.id),
                'name': ticket.ticket_type.name
            },
            'isListed': is_listed,
            'listingId': listing_id
        }
        items.append(ticket_dict)

    # 5. Devolver la respuesta paginada que el frontend espera
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }