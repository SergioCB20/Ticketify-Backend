"""
Script para eliminar listings del marketplace.
Útil para limpiar datos de prueba o corregir problemas.

OPCIONES:
1. Eliminar TODOS los listings
2. Eliminar solo listings ACTIVOS
3. Eliminar listings de un usuario específico
4. Eliminar listings y sus tickets asociados

USO:
    python -m app.scripts.delete_marketplace_listings
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


def delete_all_listings(db: Session, delete_tickets: bool = False):
    """
    Elimina TODOS los listings del marketplace.
    
    Args:
        db: Sesión de base de datos
        delete_tickets: Si es True, también elimina los tickets asociados
    """
    try:
        listings = db.query(MarketplaceListing).all()
        count = len(listings)
        
        print(f"📋 Encontrados {count} listings en total")
        
        if count == 0:
            print("✅ No hay listings para eliminar.")
            return
        
        if delete_tickets:
            print("⚠️  También se eliminarán los tickets asociados...")
            for listing in listings:
                ticket = db.query(Ticket).filter(Ticket.id == listing.ticket_id).first()
                if ticket:
                    db.delete(ticket)
        
        for listing in listings:
            db.delete(listing)
        
        db.commit()
        print(f"✅ {count} listings eliminados exitosamente.")
        
        if delete_tickets:
            print(f"✅ Tickets asociados también eliminados.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise


def delete_active_listings(db: Session, restore_tickets: bool = True):
    """
    Elimina solo los listings ACTIVOS del marketplace.
    Opcionalmente restaura los tickets a estado ACTIVE.
    
    Args:
        db: Sesión de base de datos
        restore_tickets: Si es True, restaura los tickets a ACTIVE
    """
    try:
        listings = db.query(MarketplaceListing).filter(
            MarketplaceListing.status == ListingStatus.ACTIVE
        ).all()
        
        count = len(listings)
        print(f"📋 Encontrados {count} listings ACTIVOS")
        
        if count == 0:
            print("✅ No hay listings activos para eliminar.")
            return
        
        for listing in listings:
            if restore_tickets:
                ticket = db.query(Ticket).filter(Ticket.id == listing.ticket_id).first()
                if ticket:
                    ticket.status = TicketStatus.ACTIVE
                    ticket.isValid = True
                    db.add(ticket)
                    print(f"  ♻️  Ticket {ticket.id} restaurado a ACTIVE")
            
            db.delete(listing)
            print(f"  🗑️  Listing {listing.id} eliminado")
        
        db.commit()
        print(f"\n✅ {count} listings activos eliminados.")
        
        if restore_tickets:
            print(f"✅ {count} tickets restaurados a estado ACTIVE.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise


def delete_user_listings(db: Session, user_email: str, restore_tickets: bool = True):
    """
    Elimina los listings de un usuario específico.
    
    Args:
        db: Sesión de base de datos
        user_email: Email del usuario
        restore_tickets: Si es True, restaura los tickets a ACTIVE
    """
    try:
        from app.models.user import User
        
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            print(f"❌ Usuario con email '{user_email}' no encontrado.")
            return
        
        listings = db.query(MarketplaceListing).filter(
            MarketplaceListing.seller_id == user.id
        ).all()
        
        count = len(listings)
        print(f"📋 Encontrados {count} listings del usuario {user.fullName} ({user_email})")
        
        if count == 0:
            print("✅ Este usuario no tiene listings.")
            return
        
        for listing in listings:
            if restore_tickets:
                ticket = db.query(Ticket).filter(Ticket.id == listing.ticket_id).first()
                if ticket:
                    ticket.status = TicketStatus.ACTIVE
                    ticket.isValid = True
                    db.add(ticket)
            
            db.delete(listing)
        
        db.commit()
        print(f"✅ {count} listings eliminados.")
        
        if restore_tickets:
            print(f"✅ Tickets restaurados a estado ACTIVE.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise


def cancel_all_active_listings(db: Session):
    """
    En lugar de eliminar, marca todos los listings activos como CANCELLED.
    Esto preserva el historial.
    """
    try:
        listings = db.query(MarketplaceListing).filter(
            MarketplaceListing.status == ListingStatus.ACTIVE
        ).all()
        
        count = len(listings)
        print(f"📋 Encontrados {count} listings ACTIVOS")
        
        if count == 0:
            print("✅ No hay listings activos.")
            return
        
        for listing in listings:
            listing.status = ListingStatus.CANCELLED
            db.add(listing)
            
            # Restaurar el ticket
            ticket = db.query(Ticket).filter(Ticket.id == listing.ticket_id).first()
            if ticket:
                ticket.status = TicketStatus.ACTIVE
                ticket.isValid = True
                db.add(ticket)
        
        db.commit()
        print(f"✅ {count} listings marcados como CANCELLED.")
        print(f"✅ Tickets restaurados a estado ACTIVE.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise


def show_menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*60)
    print("ELIMINAR LISTINGS DEL MARKETPLACE")
    print("="*60)
    print()
    print("Opciones:")
    print("1. Cancelar todos los listings activos (RECOMENDADO)")
    print("2. Eliminar solo listings ACTIVOS (restaura tickets)")
    print("3. Eliminar TODOS los listings (preserva tickets)")
    print("4. Eliminar listings de un usuario específico")
    print("5. Eliminar TODO (listings + tickets)")
    print("0. Salir")
    print()


def main():
    db: Session = SessionLocal()
    
    try:
        while True:
            show_menu()
            option = input("Selecciona una opción: ").strip()
            
            if option == "0":
                print("👋 ¡Hasta luego!")
                break
            
            elif option == "1":
                print("\n🔄 CANCELAR LISTINGS ACTIVOS")
                print("Esto marcará los listings como CANCELLED y restaurará los tickets.")
                confirm = input("¿Continuar? (s/n): ").lower()
                if confirm == 's':
                    cancel_all_active_listings(db)
                else:
                    print("❌ Operación cancelada.")
            
            elif option == "2":
                print("\n🗑️  ELIMINAR LISTINGS ACTIVOS")
                print("⚠️  Esto ELIMINARÁ permanentemente los listings activos.")
                print("Los tickets serán restaurados a estado ACTIVE.")
                confirm = input("¿Continuar? (s/n): ").lower()
                if confirm == 's':
                    delete_active_listings(db, restore_tickets=True)
                else:
                    print("❌ Operación cancelada.")
            
            elif option == "3":
                print("\n🗑️  ELIMINAR TODOS LOS LISTINGS")
                print("⚠️  Esto ELIMINARÁ TODOS los listings (ACTIVOS, VENDIDOS, CANCELADOS).")
                print("Los tickets NO serán eliminados.")
                confirm = input("¿Estás SEGURO? (escribe 'CONFIRMAR'): ").strip()
                if confirm == 'CONFIRMAR':
                    delete_all_listings(db, delete_tickets=False)
                else:
                    print("❌ Operación cancelada.")
            
            elif option == "4":
                print("\n🗑️  ELIMINAR LISTINGS DE UN USUARIO")
                email = input("Email del usuario: ").strip()
                if email:
                    delete_user_listings(db, email, restore_tickets=True)
                else:
                    print("❌ Email inválido.")
            
            elif option == "5":
                print("\n⚠️⚠️⚠️  ELIMINAR TODO (LISTINGS + TICKETS) ⚠️⚠️⚠️")
                print("¡CUIDADO! Esto ELIMINARÁ permanentemente:")
                print("- Todos los listings")
                print("- Todos los tickets asociados")
                print("- No se puede deshacer")
                confirm = input("¿Estás ABSOLUTAMENTE SEGURO? (escribe 'ELIMINAR TODO'): ").strip()
                if confirm == 'ELIMINAR TODO':
                    delete_all_listings(db, delete_tickets=True)
                else:
                    print("❌ Operación cancelada.")
            
            else:
                print("❌ Opción inválida.")
            
            input("\nPresiona Enter para continuar...")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
