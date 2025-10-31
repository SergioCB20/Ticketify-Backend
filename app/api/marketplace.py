from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from typing import Optional
import math

from app.core.database import get_db
from app.models.marketplace_listing import MarketplaceListing, ListingStatus
from app.models.event import Event
from app.models.user import User
# Asume que creaste los schemas del paso 1
from app.schemas.marketplace import MarketplaceListingResponse, PaginatedMarketplaceListings

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])

@router.get("/listings", response_model=PaginatedMarketplaceListings)
async def get_active_listings(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    """
    Obtener todos los listados de reventa ACTIVOS y paginados.
    """
    try:
        # Query base: Solo listados ACTIVOS
        query = (
            select(MarketplaceListing)
            .join(MarketplaceListing.event) # Join con Evento
            .options(
                joinedload(MarketplaceListing.seller), # Cargar datos del vendedor
                joinedload(MarketplaceListing.event)   # Cargar datos del evento
            )
            .where(MarketplaceListing.status == ListingStatus.ACTIVE)
        )
        
        # Filtro de búsqueda (busca en título del listado o título del evento)
        if search:
            search_term = f"%{search.lower()}%"
            query = query.filter(
                or_(
                    func.lower(MarketplaceListing.title).like(search_term),
                    func.lower(Event.title).like(search_term)
                )
            )

        # Contar el total de items (antes de paginar)
        total_query = select(func.count()).select_from(query.subquery())
        total = db.execute(total_query).scalar()
        
        if total is None:
            total = 0

        # Calcular paginación
        total_pages = math.ceil(total / page_size)
        offset = (page - 1) * page_size
        
        # Aplicar paginación y ejecutar query
        listings = db.scalars(query.order_by(MarketplaceListing.created_at.desc()).offset(offset).limit(page_size)).all()
        
        return {
            "items": listings,
            "total": total,
            "page": page,
            "pageSize": page_size,
            "totalPages": total_pages
        }

    except Exception as e:
        print(f"Error al obtener listados del marketplace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al cargar los listados."
        )