# ticket_type_repository.py

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID

from app.models.ticket_type import TicketType
from app.schemas.ticket_type import TicketTypeCreate, TicketTypeUpdate


class TicketTypeRepository:
    """Repository for TicketType database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, ticket_type_id: UUID) -> Optional[TicketType]:
        """Get a ticket type by ID"""
        return (
            self.db.query(TicketType)
            .filter(TicketType.id == ticket_type_id)
            .first()
        )

    def get_by_event(self, event_id: UUID, active_only: bool = False) -> List[TicketType]:
        """Get all ticket types for an event"""
        query = self.db.query(TicketType).filter(TicketType.event_id == event_id)
        
        if active_only:
            query = query.filter(TicketType.is_active == True)
        
        return query.order_by(TicketType.sort_order.asc(), TicketType.price.asc()).all()

    def get_available_by_event(self, event_id: UUID) -> List[TicketType]:
        """Get all available ticket types for an event (not sold out, active, on sale)"""
        return (
            self.db.query(TicketType)
            .filter(
                TicketType.event_id == event_id,
                TicketType.is_active == True,
                TicketType.quantity_available > TicketType.sold_quantity
            )
            .order_by(TicketType.sort_order.asc(), TicketType.price.asc())
            .all()
        )

    def create(self, event_id: UUID, ticket_type_data: TicketTypeCreate) -> TicketType:
        """Create a new ticket type"""
        # Convert Pydantic model to dict, handling aliases
        data_dict = ticket_type_data.dict(by_alias=False)
        
        # Create ticket type instance
        db_ticket_type = TicketType(
            event_id=event_id,
            name=data_dict.get('name'),
            description=data_dict.get('description'),
            price=data_dict.get('price'),
            quantity_available=data_dict.get('quantity_available'),
            min_purchase=data_dict.get('min_purchase', 1),
            max_purchase=data_dict.get('max_purchase', 10),
            sale_start_date=data_dict.get('sale_start_date'),
            sale_end_date=data_dict.get('sale_end_date')
        )
        
        self.db.add(db_ticket_type)
        self.db.commit()
        self.db.refresh(db_ticket_type)
        return db_ticket_type

    def create_batch(self, event_id: UUID, ticket_types_data: List[TicketTypeCreate]) -> List[TicketType]:
        """Create multiple ticket types at once"""
        created_ticket_types = []
        
        for idx, ticket_type_data in enumerate(ticket_types_data):
            data_dict = ticket_type_data.dict(by_alias=False)
            
            db_ticket_type = TicketType(
                event_id=event_id,
                name=data_dict.get('name'),
                description=data_dict.get('description'),
                price=data_dict.get('price'),
                quantity_available=data_dict.get('quantity_available'),
                min_purchase=data_dict.get('min_purchase', 1),
                max_purchase=data_dict.get('max_purchase', 10),
                sale_start_date=data_dict.get('sale_start_date'),
                sale_end_date=data_dict.get('sale_end_date'),
                sort_order=idx  # Mantener el orden de inserción
            )
            
            self.db.add(db_ticket_type)
            created_ticket_types.append(db_ticket_type)
        
        self.db.commit()
        
        # Refresh all to get generated IDs and timestamps
        for ticket_type in created_ticket_types:
            self.db.refresh(ticket_type)
        
        return created_ticket_types

    def update(self, ticket_type_id: UUID, ticket_type_data: TicketTypeUpdate) -> Optional[TicketType]:
        """Update a ticket type"""
        ticket_type = self.get_by_id(ticket_type_id)
        
        if not ticket_type:
            return None

        # Update only provided fields
        update_data = ticket_type_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(ticket_type, field):
                setattr(ticket_type, field, value)

        self.db.commit()
        self.db.refresh(ticket_type)
        return ticket_type

    def delete(self, ticket_type_id: UUID) -> bool:
        """Delete a ticket type"""
        ticket_type = self.get_by_id(ticket_type_id)
        
        if not ticket_type:
            return False

        self.db.delete(ticket_type)
        self.db.commit()
        return True

    def increment_sold_quantity(self, ticket_type_id: UUID, quantity: int = 1) -> Optional[TicketType]:
        """Increment the sold quantity when tickets are purchased"""
        ticket_type = self.get_by_id(ticket_type_id)
        
        if not ticket_type:
            return None
        
        # Check if there's enough availability
        if ticket_type.remaining_quantity < quantity:
            return None
        
        ticket_type.sold_quantity += quantity
        self.db.commit()
        self.db.refresh(ticket_type)
        return ticket_type

    def decrement_sold_quantity(self, ticket_type_id: UUID, quantity: int = 1) -> Optional[TicketType]:
        """Decrement the sold quantity (e.g., on refund)"""
        ticket_type = self.get_by_id(ticket_type_id)
        
        if not ticket_type:
            return None
        
        ticket_type.sold_quantity = max(0, ticket_type.sold_quantity - quantity)
        self.db.commit()
        self.db.refresh(ticket_type)
        return ticket_type

    def toggle_active(self, ticket_type_id: UUID, is_active: bool) -> Optional[TicketType]:
        """Toggle the active status of a ticket type"""
        ticket_type = self.get_by_id(ticket_type_id)
        
        if not ticket_type:
            return None
        
        ticket_type.is_active = is_active
        self.db.commit()
        self.db.refresh(ticket_type)
        return ticket_type
