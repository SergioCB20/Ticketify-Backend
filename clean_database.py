# -*- coding: utf-8 -*-
"""
Script para limpiar datos de prueba de la base de datos
¡CUIDADO! Este script borra datos. Usar solo en desarrollo.
"""

from app.core.database import SessionLocal
from app.models import (
    User, Event, EventCategory, TicketType, Role, Permission,
    Ticket, Payment, Purchase, MarketplaceListing, Notification
)

def confirm_action():
    """Pedir confirmación antes de borrar datos"""
    print("⚠️  " + "=" * 68)
    print("⚠️  ADVERTENCIA: Este script borrará TODOS los datos de la base de datos")
    print("⚠️  " + "=" * 68)
    print()
    print("Esta acción es IRREVERSIBLE y borrará:")
    print("  - Todos los usuarios")
    print("  - Todos los eventos")
    print("  - Todos los tickets")
    print("  - Todos los pagos")
    print("  - Todas las compras")
    print("  - Todas las notificaciones")
    print("  - (Mantendrá roles, permisos y categorías)")
    print()
    
    response = input("¿Estás seguro que quieres continuar? Escribe 'SI BORRAR' para confirmar: ")
    
    return response == "SI BORRAR"


def clean_test_data():
    """Limpiar datos de prueba manteniendo estructura base"""
    db = SessionLocal()
    
    try:
        print("\n🧹 Iniciando limpieza de datos de prueba...\n")
        
        # Borrar en orden (respetando foreign keys)
        print("📋 Borrando notificaciones...")
        deleted = db.query(Notification).delete()
        print(f"   ✓ {deleted} notificaciones eliminadas")
        
        print("📋 Borrando marketplace listings...")
        deleted = db.query(MarketplaceListing).delete()
        print(f"   ✓ {deleted} listings eliminados")
        
        print("📋 Borrando tickets...")
        deleted = db.query(Ticket).delete()
        print(f"   ✓ {deleted} tickets eliminados")
        
        print("📋 Borrando pagos...")
        deleted = db.query(Payment).delete()
        print(f"   ✓ {deleted} pagos eliminados")
        
        print("📋 Borrando tipos de tickets...")
        deleted = db.query(TicketType).delete()
        print(f"   ✓ {deleted} tipos de tickets eliminados")
        
        print("📋 Borrando eventos...")
        deleted = db.query(Event).delete()
        print(f"   ✓ {deleted} eventos eliminados")
        
        print("📋 Borrando usuarios...")
        deleted = db.query(User).delete()
        print(f"   ✓ {deleted} usuarios eliminados")
        
        db.commit()
        
        print("\n✅ Limpieza completada exitosamente!")
        print("\n📊 Estado actual:")
        print(f"   - Roles: {db.query(Role).count()}")
        print(f"   - Permisos: {db.query(Permission).count()}")
        print(f"   - Categorías: {db.query(EventCategory).count()}")
        print(f"   - Usuarios: {db.query(User).count()}")
        print(f"   - Eventos: {db.query(Event).count()}")
        
        print("\n💡 Para volver a crear los datos de prueba, ejecuta:")
        print("   python seed_all.py")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def clean_everything():
    """Limpiar ABSOLUTAMENTE TODO incluyendo roles y categorías"""
    db = SessionLocal()
    
    try:
        print("\n🧹 Iniciando limpieza COMPLETA de la base de datos...\n")
        
        # Borrar en orden (respetando foreign keys)
        print("📋 Borrando notificaciones...")
        deleted = db.query(Notification).delete()
        print(f"   ✓ {deleted} notificaciones eliminadas")
        
        print("📋 Borrando marketplace listings...")
        deleted = db.query(MarketplaceListing).delete()
        print(f"   ✓ {deleted} listings eliminados")
        
        print("📋 Borrando tickets...")
        deleted = db.query(Ticket).delete()
        print(f"   ✓ {deleted} tickets eliminados")
        
        print("📋 Borrando pagos...")
        deleted = db.query(Payment).delete()
        print(f"   ✓ {deleted} pagos eliminados")
        
        print("📋 Borrando tipos de tickets...")
        deleted = db.query(TicketType).delete()
        print(f"   ✓ {deleted} tipos de tickets eliminados")
        
        print("📋 Borrando eventos...")
        deleted = db.query(Event).delete()
        print(f"   ✓ {deleted} eventos eliminados")
        
        print("📋 Borrando usuarios...")
        deleted = db.query(User).delete()
        print(f"   ✓ {deleted} usuarios eliminados")
        
        print("📋 Borrando categorías...")
        deleted = db.query(EventCategory).delete()
        print(f"   ✓ {deleted} categorías eliminadas")
        
        print("📋 Borrando roles...")
        deleted = db.query(Role).delete()
        print(f"   ✓ {deleted} roles eliminados")
        
        print("📋 Borrando permisos...")
        deleted = db.query(Permission).delete()
        print(f"   ✓ {deleted} permisos eliminados")
        
        db.commit()
        
        print("\n✅ Limpieza COMPLETA exitosa!")
        print("\n⚠️  La base de datos está completamente vacía.")
        print("\n💡 Para recrear todo desde cero, ejecuta:")
        print("   python seed_all.py")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Menú principal"""
    print("\n" + "=" * 70)
    print("🧹 SCRIPT DE LIMPIEZA DE BASE DE DATOS")
    print("=" * 70)
    print()
    print("Selecciona una opción:")
    print()
    print("1. Limpiar solo datos de prueba (mantiene roles y categorías)")
    print("2. Limpiar TODO (incluye roles, permisos y categorías)")
    print("3. Cancelar")
    print()
    
    choice = input("Ingresa tu opción (1-3): ")
    
    if choice == "1":
        if confirm_action():
            clean_test_data()
        else:
            print("\n❌ Operación cancelada por el usuario")
    elif choice == "2":
        print("\n⚠️  ¡Atención! Esta opción borra ABSOLUTAMENTE TODO")
        if confirm_action():
            clean_everything()
        else:
            print("\n❌ Operación cancelada por el usuario")
    elif choice == "3":
        print("\n✅ Operación cancelada")
    else:
        print("\n❌ Opción inválida")


if __name__ == "__main__":
    main()
