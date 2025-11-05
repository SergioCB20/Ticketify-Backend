# ticket_type_service.py

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.repositories.ticket_type_repository import TicketTypeRepository
from app.repositories.event_repository import EventRepository
from app.schemas.ticket_type import (
    TicketTypeCreate,
    TicketTypeUpdate,
    TicketTypeResponse
)
from app.models.ticket_type import TicketType


class TicketTypeService:
    """Ticket Type service with business logic"""

    def __init__(self, db: Session):
        self.db = db
        self.ticket_type_repo = TicketTypeRepository(db)
        self.event_repo = EventRepository(db)

    def _ticket_type_to_response(self, ticket_type: TicketType) -> Dict[str, Any]:
        """Convert TicketType model to response dictionary"""
        return {
            "id": ticket_type.id,
            "eventId": ticket_type.event_id,
            "name": ticket_type.name,
            "description": ticket_type.description,
            "price": float(ticket_type.price) if ticket_type.price else 0,
            "originalPrice": float(ticket_type.original_price) if ticket_type.original_price else None,
            "quantityAvailable": ticket_type.quantity_available,
            "soldQuantity": ticket_type.sold_quantity,
            "remainingQuantity": ticket_type.remaining_quantity,
            "minPurchase": ticket_type.min_purchase,
            "maxPurchase": ticket_type.max_purchase,
            "saleStartDate": ticket_type.sale_start_date,
            "saleEndDate": ticket_type.sale_end_date,
            "isActive": ticket_type.is_active,
            "isFeatured": ticket_type.is_featured,
            "isSoldOut": ticket_type.is_sold_out,
            "isOnSale": ticket_type.is_on_sale,
            "sortOrder": ticket_type.sort_order,
            "createdAt": ticket_type.created_at,
            "updatedAt": ticket_type.updated_at
        }

    def get_ticket_types_by_event(
        self, 
        event_id: UUID, 
        active_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all ticket types for an event"""
        # Verify event exists
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        ticket_types = self.ticket_type_repo.get_by_event(event_id, active_only)
        return [self._ticket_type_to_response(tt) for tt in ticket_types]

    def get_ticket_type_by_id(self, ticket_type_id: UUID) -> TicketTypeResponse:
        """Get a single ticket type by ID"""
        ticket_type = self.ticket_type_repo.get_by_id(ticket_type_id)

        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )

        return TicketTypeResponse(**self._ticket_type_to_response(ticket_type))

    def create_ticket_type(
        self, 
        event_id: UUID, 
        ticket_type_data: TicketTypeCreate
    ) -> TicketTypeResponse:
        """Create a new ticket type for an event"""
        # Verify event exists
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        # Create ticket type
        ticket_type = self.ticket_type_repo.create(event_id, ticket_type_data)

        return TicketTypeResponse(**self._ticket_type_to_response(ticket_type))

    def create_ticket_types_batch(
        self, 
        event_id: UUID, 
        ticket_types_data: List[TicketTypeCreate]
    ) -> List[TicketTypeResponse]:
        """Create multiple ticket types at once"""
        # Verify event exists
        event = self.event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )

        # Validate total capacity
        total_ticket_capacity = sum(tt.quantity_available for tt in ticket_types_data)
        if total_ticket_capacity > event.totalCapacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La suma de capacidades de los tipos de entrada ({total_ticket_capacity}) "
                       f"no puede superar la capacidad total del evento ({event.totalCapacity})"
            )

        # Create all ticket types
        ticket_types = self.ticket_type_repo.create_batch(event_id, ticket_types_data)

        return [TicketTypeResponse(**self._ticket_type_to_response(tt)) for tt in ticket_types]

    def update_ticket_type(
        self, 
        ticket_type_id: UUID, 
        ticket_type_data: TicketTypeUpdate
    ) -> TicketTypeResponse:
        """Update a ticket type"""
        # Check if ticket type exists
        existing = self.ticket_type_repo.get_by_id(ticket_type_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )

        # Update ticket type
        updated_ticket_type = self.ticket_type_repo.update(ticket_type_id, ticket_type_data)

        if not updated_ticket_type:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al actualizar el tipo de entrada"
            )

        return TicketTypeResponse(**self._ticket_type_to_response(updated_ticket_type))

    def delete_ticket_type(self, ticket_type_id: UUID) -> Dict[str, str]:
        """Delete a ticket type"""
        # Check if ticket type exists
        ticket_type = self.ticket_type_repo.get_by_id(ticket_type_id)
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )

        # Check if any tickets have been sold
        if ticket_type.sold_quantity > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el tipo de entrada porque ya se han vendido {ticket_type.sold_quantity} tickets"
            )

        # Delete ticket type
        success = self.ticket_type_repo.delete(ticket_type_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el tipo de entrada"
            )

        return {"message": "Tipo de entrada eliminado exitosamente"}

    def toggle_ticket_type_status(
        self, 
        ticket_type_id: UUID, 
        is_active: bool
    ) -> TicketTypeResponse:
        """Toggle the active status of a ticket type"""
        ticket_type = self.ticket_type_repo.toggle_active(ticket_type_id, is_active)

        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )

        return TicketTypeResponse(**self._ticket_type_to_response(ticket_type))
