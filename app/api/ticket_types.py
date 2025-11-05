# ticket_types.py (API Layer)

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.dependencies import get_db
from app.services.ticket_type_service import TicketTypeService
from app.schemas.ticket_type import (
    TicketTypeResponse,
    TicketTypeCreate,
    TicketTypeUpdate,
    TicketTypeBatchCreate
)

router = APIRouter(prefix="/ticket-types", tags=["Ticket Types"])


# --- Dependency Injection ---

def get_ticket_type_service(db: Session = Depends(get_db)) -> TicketTypeService:
    """Dependency to inject the ticket type service"""
    return TicketTypeService(db)


# --- Endpoints ---

@router.get("/event/{event_id}", response_model=List[TicketTypeResponse])
def get_ticket_types_by_event(
    event_id: UUID,
    active_only: bool = Query(False, description="Mostrar solo tipos de entrada activos"),
    ticket_type_service: TicketTypeService = Depends(get_ticket_type_service)
):
    """
    Obtener todos los tipos de entrada de un evento específico.
    
    - **event_id**: ID del evento
    - **active_only**: Si es True, solo devuelve tipos de entrada activos
    """
    return ticket_type_service.get_ticket_types_by_event(event_id, active_only)


@router.get("/{ticket_type_id}", response_model=TicketTypeResponse)
def get_ticket_type(
    ticket_type_id: UUID,
    ticket_type_service: TicketTypeService = Depends(get_ticket_type_service)
):
    """
    Obtener un tipo de entrada específico por su ID.
    """
    return ticket_type_service.get_ticket_type_by_id(ticket_type_id)


@router.post("/event/{event_id}", response_model=TicketTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_type(
    event_id: UUID,
    ticket_type_data: TicketTypeCreate,
    ticket_type_service: TicketTypeService = Depends(get_ticket_type_service)
):
    """
    Crear un nuevo tipo de entrada para un evento.
    Requiere permisos de organizador del evento.
    """
    return ticket_type_service.create_ticket_type(event_id, ticket_type_data)


@router.post("/batch", response_model=List[TicketTypeResponse], status_code=status.HTTP_201_CREATED)
def create_ticket_types_batch(
    batch_data: TicketTypeBatchCreate,
    ticket_type_service: TicketTypeService = Depends(get_ticket_type_service)
):
    """
    Crear múltiples tipos de entrada a la vez para un evento.
    Útil al crear un evento nuevo con varios tipos de entrada.
    
    Valida que la suma de capacidades no supere la capacidad total del evento.
    """
    return ticket_type_service.create_ticket_types_batch(
        batch_data.eventId, 
        batch_data.ticketTypes
    )


@router.put("/{ticket_type_id}", response_model=TicketTypeResponse)
def update_ticket_type(
    ticket_type_id: UUID,
    ticket_type_data: TicketTypeUpdate,
    ticket_type_service: TicketTypeService = Depends(get_ticket_type_service)
):
    """
    Actualizar un tipo de entrada existente.
    Requiere permisos de organizador del evento.
    """
    return ticket_type_service.update_ticket_type(ticket_type_id, ticket_type_data)


@router.patch("/{ticket_type_id}/status", response_model=TicketTypeResponse)
def toggle_ticket_type_status(
    ticket_type_id: UUID,
    is_active: bool = Query(..., description="Nuevo estado activo/inactivo"),
    ticket_type_service: TicketTypeService = Depends(get_ticket_type_service)
):
    """
    Activar o desactivar un tipo de entrada.
    Útil para pausar la venta de un tipo específico sin eliminarlo.
    """
    return ticket_type_service.toggle_ticket_type_status(ticket_type_id, is_active)


@router.delete("/{ticket_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_type(
    ticket_type_id: UUID,
    ticket_type_service: TicketTypeService = Depends(get_ticket_type_service)
):
    """
    Eliminar un tipo de entrada.
    No se puede eliminar si ya se han vendido tickets de este tipo.
    Requiere permisos de organizador del evento.
    """
    ticket_type_service.delete_ticket_type(ticket_type_id)
    return None
