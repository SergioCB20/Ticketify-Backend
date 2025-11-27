from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
from uuid import UUID

from app.repositories.ticket_type_repository import TicketTypeRepository
from app.repositories.event_repository import EventRepository
from app.schemas.ticket_type import (
    TicketTypeCreate, 
    TicketTypeUpdate, 
    TicketTypeResponse,
    TicketTypeUpdateItem
)
from app.models.ticket_type import TicketType
from app.models.event import Event



class TicketTypeService:
    """Service layer for ticket type business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ticket_type_repo = TicketTypeRepository(db)
        self.event_repo = EventRepository(db)
    
    def create_ticket_type(
        self, 
        event_id: UUID, 
        ticket_type_data: TicketTypeCreate
    ) -> TicketTypeResponse:
        """Create a new ticket type for an event"""
        # Verify event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Verify total capacity
        current_capacity = self.ticket_type_repo.get_total_capacity_by_event(event_id)
        new_capacity = current_capacity + ticket_type_data.quantity
        
        if new_capacity > event.totalCapacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La suma de capacidades de tipos de entrada ({new_capacity}) supera la capacidad total del evento ({event.totalCapacity})"
            )
        
        # Create ticket type
        ticket_type = self.ticket_type_repo.create_ticket_type(event_id, ticket_type_data)
        
        return self._ticket_type_to_response(ticket_type)
    
    def create_ticket_types_batch(
        self, 
        event_id: UUID, 
        ticket_types_data: List[TicketTypeCreate]
    ) -> List[TicketTypeResponse]:
        """Create multiple ticket types for an event"""
        # Verify event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        # Validate total capacity
        total_ticket_capacity = sum(tt.quantity for tt in ticket_types_data)
        
        if total_ticket_capacity > event.totalCapacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La suma de capacidades de tipos de entrada ({total_ticket_capacity}) supera la capacidad total del evento ({event.totalCapacity})"
            )
        
        # Create ticket types
        ticket_types = self.ticket_type_repo.create_ticket_types_batch(
            event_id, 
            ticket_types_data
        )
        
        return [self._ticket_type_to_response(tt) for tt in ticket_types]

    def update_ticket_types_batch(self, event_id: UUID, items: List[TicketTypeUpdate]):
        event = self.db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(404, "Evento no encontrado")

        existing = {
            str(t.id): t
            for t in self.db.query(TicketType).filter(TicketType.event_id == event_id).all()
        }

        ids_sent = set()

        for it in items:
            if it.id:
                # ACTUALIZAR
                tt = existing.get(str(it.id))
                if not tt:
                    continue

                tt.name = it.name
                tt.description = it.description
                tt.price = it.price
                tt.quantity_available = it.quantity
                tt.max_purchase = it.maxPerPurchase
            else:
                # CREAR NUEVO
                new_tt = TicketType(
                    event_id=event_id,
                    name=it.name,
                    description=it.description,
                    price=it.price,
                    quantity_available=it.quantity,
                    sold_quantity=0,
                    max_purchase=it.maxPerPurchase,
                    min_purchase=1,
                    is_active=True,
                )
                self.db.add(new_tt)
                self.db.flush()
                ids_sent.add(str(new_tt.id))

         # ELIMINAR los que ya no existen en el payload
        for tt_id, tt in existing.items():
            if tt_id not in ids_sent:
                # si ya tiene vendidas, no lo borres
                if tt.sold_quantity and tt.sold_quantity > 0:
                    continue
                self.db.delete(tt)

        self.db.commit()
        return self.get_ticket_types_by_event(event_id, active_only=False)
    
    def get_ticket_type_by_id(self, ticket_type_id: UUID) -> TicketTypeResponse:
        """Get ticket type by ID"""
        ticket_type = self.ticket_type_repo.get_ticket_type_by_id(ticket_type_id)
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )
        
        return self._ticket_type_to_response(ticket_type)
    
    def get_ticket_types_by_event(
        self, 
        event_id: UUID, 
        active_only: bool = False
    ) -> List[TicketTypeResponse]:
        """Get all ticket types for an event"""
        # Verify event exists
        event = self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evento no encontrado"
            )
        
        ticket_types = self.ticket_type_repo.get_ticket_types_by_event(
            event_id, 
            active_only
        )
        
        return [self._ticket_type_to_response(tt) for tt in ticket_types]
    
    def update_ticket_type(
        self, 
        ticket_type_id: UUID, 
        ticket_type_data: TicketTypeUpdate
    ) -> TicketTypeResponse:
        """Update ticket type"""
        ticket_type = self.ticket_type_repo.get_ticket_type_by_id(ticket_type_id)
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )
        
        # If updating quantity, validate against event capacity
        if ticket_type_data.quantity_available is not None:
            event = self.event_repo.get_event_by_id(ticket_type.event_id)
            current_capacity = self.ticket_type_repo.get_total_capacity_by_event(
                ticket_type.event_id
            )
            # Subtract current ticket type capacity and add new capacity
            new_total = current_capacity - ticket_type.quantity_available + ticket_type_data.quantity_available
            
            if new_total > event.totalCapacity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"La nueva capacidad total ({new_total}) supera la capacidad del evento ({event.totalCapacity})"
                )
        
        updated_ticket_type = self.ticket_type_repo.update_ticket_type(
            ticket_type_id, 
            ticket_type_data
        )
        
        return self._ticket_type_to_response(updated_ticket_type)
    
    def toggle_ticket_type_status(
        self, 
        ticket_type_id: UUID, 
        is_active: bool
    ) -> TicketTypeResponse:
        """Activate or deactivate a ticket type"""
        ticket_type = self.ticket_type_repo.get_ticket_type_by_id(ticket_type_id)
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )
        
        updated_ticket_type = self.ticket_type_repo.toggle_ticket_type_status(
            ticket_type_id, 
            is_active
        )
        
        return self._ticket_type_to_response(updated_ticket_type)
    
    def delete_ticket_type(self, ticket_type_id: UUID) -> None:
        """Delete ticket type"""
        ticket_type = self.ticket_type_repo.get_ticket_type_by_id(ticket_type_id)
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de entrada no encontrado"
            )
        
        # Check if any tickets have been sold
        if ticket_type.sold_quantity > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un tipo de entrada con tickets vendidos"
            )
        
        success = self.ticket_type_repo.delete_ticket_type(ticket_type_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al eliminar el tipo de entrada"
            )
    
    def _ticket_type_to_response(self, ticket_type: TicketType) -> TicketTypeResponse:
        """Convert TicketType model to TicketTypeResponse"""
        return TicketTypeResponse(
            id=ticket_type.id,
            eventId=ticket_type.event_id,
            name=ticket_type.name,
            description=ticket_type.description,
            price=float(ticket_type.price),
            originalPrice=float(ticket_type.original_price) if ticket_type.original_price else None,
            quantityAvailable=ticket_type.quantity_available,
            soldQuantity=ticket_type.sold_quantity,
            remainingQuantity=ticket_type.remaining_quantity,
            minPurchase=ticket_type.min_purchase,
            maxPurchase=ticket_type.max_purchase,
            saleStartDate=ticket_type.sale_start_date,
            saleEndDate=ticket_type.sale_end_date,
            isActive=ticket_type.is_active,
            isFeatured=ticket_type.is_featured,
            isSoldOut=ticket_type.is_sold_out,
            isOnSale=ticket_type.is_on_sale,
            sortOrder=ticket_type.sort_order,
            createdAt=ticket_type.created_at,
            updatedAt=ticket_type.updated_at
        )
