"""
Script para corregir tickets que están en el marketplace con status TRANSFERRED.
Esto corrige el problema de los tickets que fueron publicados antes del fix.

USO:
    python -m app.scripts.fix_marketplace_tickets
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.ticket import Ticket, TicketStatus
from app.models.marketplace_listing import MarketplaceListing, ListingStatus


def fix_marketplace_tickets():
    """
    Encuentra todos los tickets con status TRANSFERRED que tienen un 
    listing ACTIVO y los cambia a status ACTIVE.
    """
    db: Session = SessionLocal()
    
    try:
        print("🔍 Buscando tickets en marketplace con status incorrecto...")
        
        # Buscar todos los listings ACTIVOS
        active_listings = db.query(MarketplaceListing).filter(
            MarketplaceListing.status == ListingStatus.ACTIVE
        ).all()
        
        print(f"📋 Encontrados {len(active_listings)} listings activos")
        
        fixed_count = 0
        
        for listing in active_listings:
            ticket = db.query(Ticket).filter(Ticket.id == listing.ticket_id).first()
            
            if ticket and ticket.status == TicketStatus.TRANSFERRED:
                print(f"✅ Corrigiendo ticket {ticket.id} (Evento: {listing.event_id})")
                ticket.status = TicketStatus.ACTIVE
                ticket.isValid = True
                db.add(ticket)
                fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
            print(f"\n🎉 ¡Corrección completada! {fixed_count} tickets actualizados.")
        else:
            print("\n✅ No se encontraron tickets que necesiten corrección.")
            
    except Exception as e:
        print(f"❌ Error durante la corrección: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT DE CORRECCIÓN DE TICKETS EN MARKETPLACE")
    print("=" * 60)
    print()
    
    confirm = input("¿Deseas continuar? (s/n): ").lower()
    
    if confirm == 's':
        fix_marketplace_tickets()
    else:
        print("❌ Operación cancelada.")
