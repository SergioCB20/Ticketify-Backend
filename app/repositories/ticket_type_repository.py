from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.ticket_type import TicketType
from app.schemas.ticket_type import TicketTypeCreate, TicketTypeUpdate


class TicketTypeRepository:
    """Repository for TicketType database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_ticket_type(self, event_id: UUID, ticket_type_data: TicketTypeCreate) -> TicketType:
        """Create a new ticket type"""
        ticket_type = TicketType(
            event_id=event_id,
            name=ticket_type_data.name,
            description=ticket_type_data.description,
            price=ticket_type_data.price,
            quantity_available=ticket_type_data.quantity,
            min_purchase=ticket_type_data.min_purchase,
            max_purchase=ticket_type_data.max_purchase,
            sale_start_date=ticket_type_data.sale_start_date,
            sale_end_date=ticket_type_data.sale_end_date,
            is_active=True,
            sold_quantity=0
        )
        
        self.db.add(ticket_type)
        self.db.commit()
        self.db.refresh(ticket_type)
        return ticket_type
    
    def create_ticket_types_batch(self, event_id: UUID, ticket_types_data: List[TicketTypeCreate]) -> List[TicketType]:
        """Create multiple ticket types for an event"""
        ticket_types = []
        
        for idx, ticket_type_data in enumerate(ticket_types_data):
            ticket_type = TicketType(
                event_id=event_id,
                name=ticket_type_data.name,
                description=ticket_type_data.description,
                price=ticket_type_data.price,
                quantity_available=ticket_type_data.quantity,
                min_purchase=ticket_type_data.min_purchase,
                max_purchase=ticket_type_data.max_purchase,
                sale_start_date=ticket_type_data.sale_start_date,
                sale_end_date=ticket_type_data.sale_end_date,
                is_active=True,
                sold_quantity=0,
                sort_order=idx
            )
            ticket_types.append(ticket_type)
        
        self.db.add_all(ticket_types)
        self.db.commit()
        
        for ticket_type in ticket_types:
            self.db.refresh(ticket_type)
        
        return ticket_types
    
    def get_ticket_type_by_id(self, ticket_type_id: UUID) -> Optional[TicketType]:
        """Get ticket type by ID"""
        return self.db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
    
    def get_ticket_types_by_event(
        self, 
        event_id: UUID, 
        active_only: bool = False
    ) -> List[TicketType]:
        """Get all ticket types for an event"""
        query = self.db.query(TicketType).filter(TicketType.event_id == event_id)
        
        if active_only:
            query = query.filter(TicketType.is_active == True)
        
        return query.order_by(TicketType.sort_order.asc()).all()
    
    def update_ticket_type(
        self, 
        ticket_type_id: UUID, 
        ticket_type_data: TicketTypeUpdate
    ) -> Optional[TicketType]:
        """Update ticket type"""
        ticket_type = self.get_ticket_type_by_id(ticket_type_id)
        if not ticket_type:
            return None
        
        # Update only provided fields
        update_data = ticket_type_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ticket_type, field, value)
        
        self.db.commit()
        self.db.refresh(ticket_type)
        return ticket_type
    
    def toggle_ticket_type_status(self, ticket_type_id: UUID, is_active: bool) -> Optional[TicketType]:
        """Activate or deactivate a ticket type"""
        ticket_type = self.get_ticket_type_by_id(ticket_type_id)
        if not ticket_type:
            return None
        
        ticket_type.is_active = is_active
        self.db.commit()
        self.db.refresh(ticket_type)
        return ticket_type
    
    def delete_ticket_type(self, ticket_type_id: UUID) -> bool:
        """Delete ticket type (only if no tickets sold)"""
        ticket_type = self.get_ticket_type_by_id(ticket_type_id)
        if not ticket_type:
            return False
        
        # Check if any tickets have been sold
        if ticket_type.sold_quantity > 0:
            return False
        
        self.db.delete(ticket_type)
        self.db.commit()
        return True
    
    def get_total_capacity_by_event(self, event_id: UUID) -> int:
        """Get total capacity configured across all ticket types for an event"""
        ticket_types = self.get_ticket_types_by_event(event_id)
        return sum(tt.quantity_available for tt in ticket_types)
