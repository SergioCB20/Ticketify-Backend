"""
Script RÁPIDO para limpiar el marketplace completamente.
Elimina todos los listings activos y restaura los tickets.

USO:
    python -m app.scripts.quick_clean_marketplace
"""

import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.ticket import Ticket, TicketStatus
from app.models.marketplace_listing import MarketplaceListing, ListingStatus


def quick_clean():
    """Limpia rápidamente el marketplace"""
    db: Session = SessionLocal()
    
    try:
        print("🧹 Limpiando marketplace...")
        
        # Obtener todos los listings activos
        active_listings = db.query(MarketplaceListing).filter(
            MarketplaceListing.status == ListingStatus.ACTIVE
        ).all()
        
        count = len(active_listings)
        
        if count == 0:
            print("✅ No hay listings activos. El marketplace está limpio.")
            return
        
        print(f"📋 Encontrados {count} listings activos")
        
        # Restaurar tickets y eliminar listings
        for listing in active_listings:
            # Restaurar el ticket
            ticket = db.query(Ticket).filter(Ticket.id == listing.ticket_id).first()
            if ticket:
                ticket.status = TicketStatus.ACTIVE
                ticket.isValid = True
                db.add(ticket)
            
            # Eliminar el listing
            db.delete(listing)
        
        db.commit()
        
        print(f"✅ {count} listings eliminados")
        print(f"✅ {count} tickets restaurados a ACTIVE")
        print("🎉 ¡Marketplace limpio!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("LIMPIEZA RÁPIDA DEL MARKETPLACE")
    print("="*60)
    print()
    print("Esto hará:")
    print("✓ Eliminar todos los listings ACTIVOS")
    print("✓ Restaurar los tickets a estado ACTIVE")
    print()
    
    confirm = input("¿Continuar? (s/n): ").lower()
    
    if confirm == 's':
        quick_clean()
    else:
        print("❌ Operación cancelada.")
