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

@router.get("/my-tickets", response_model=List[MyTicketResponse])
async def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtiene todos los tickets activos (o en reventa) que posee el usuario actual.
    """
    
    # --- INICIO DE LA CORRECCIÓN ---

    # 1. Definir la subconsulta correlacionada (la variable que faltaba)
    #    Esta subconsulta buscará una 'MarketplaceListing' ACTIVA
    #    que esté vinculada al 'Ticket.id' de la fila actual.
    is_listed_subquery = (
        select(
            exists().where(
                MarketplaceListing.ticket_id == Ticket.id,
                MarketplaceListing.status == ListingStatus.ACTIVE
            )
        )
        .scalar_subquery()  # La convierte en un valor escalar (True/False)
    )

    # 2. Construir la consulta principal
    #    Seleccionamos el objeto Ticket y el resultado de la subconsulta (que llamamos "is_listed")
    query = (
        select(Ticket, is_listed_subquery.label("is_listed"))
        .options(
            joinedload(Ticket.event),
            joinedload(Ticket.ticket_type)
        )
        .where(
            Ticket.user_id == current_user.id,
            # (He comentado esto para que puedas ver TODOS tus tickets,
            #  incluso los usados o expirados, pero puedes descomentarlo)
            # Ticket.status.in_([TicketStatus.ACTIVE, TicketStatus.TRANSFERRED])
        )
        .order_by(Ticket.purchaseDate.desc())
    )
    
    # 3. Ejecutar la consulta
    #    'results' será una lista de tuplas: [(Ticket_obj_1, True), (Ticket_obj_2, False), ...]
    results = db.execute(query).all()
    
    # 4. Procesar los resultados para el schema de respuesta
    #    Iteramos sobre las tuplas (Ticket, bool) y asignamos el booleano
    #    al objeto ticket ANTES de retornarlo.
    response = []
    for ticket, is_listed in results:
        # Asignamos el atributo 'is_listed' al objeto ticket
        # Pydantic (tu schema) lo leerá gracias a 'from_attributes = True'
        ticket.is_listed = is_listed 
        response.append(ticket)

    return response
    # --- FIN DE LA CORRECCIÓN ---