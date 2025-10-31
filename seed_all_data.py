# -*- coding: utf-8 -*-
"""
Script maestro para ejecutar todos los seeders en el orden correcto
"""

import sys
from seed_initial_data import main as seed_initial
from seed_users_data import main as seed_users
from seed_events_data import main as seed_events


def main():
    """Ejecutar todos los seeders en orden"""
    print("\n" + "=" * 80)
    print("🚀 TICKETIFY - SCRIPT DE SEEDING COMPLETO")
    print("=" * 80)
    
    try:
        print("\n📦 PASO 1: Seeding inicial (Roles, Permisos, Categorías)")
        print("-" * 80)
        seed_initial()
        
        print("\n\n👥 PASO 2: Creando usuarios asistentes")
        print("-" * 80)
        seed_users()
        
        print("\n\n🎫 PASO 3: Creando eventos y organizadores")
        print("-" * 80)
        seed_events()
        
        print("\n\n" + "=" * 80)
        print("🎉 ¡SEEDING COMPLETADO EXITOSAMENTE!")
        print("=" * 80)
        
        print("\n📊 RESUMEN:")
        print("   ✓ Roles y permisos del sistema")
        print("   ✓ 10 categorías de eventos")
        print("   ✓ 4 organizadores de eventos")
        print("   ✓ 10 usuarios asistentes")
        print("   ✓ 17 eventos con múltiples tipos de tickets")
        
        print("\n🔐 CREDENCIALES DE PRUEBA:")
        print("\n   ORGANIZADORES:")
        print("   • organizer1@ticketify.com : Organizer123!")
        print("   • organizer2@ticketify.com : Organizer123!")
        print("   • organizer3@ticketify.com : Organizer123!")
        print("   • organizer4@ticketify.com : Organizer123!")
        
        print("\n   USUARIOS:")
        print("   • user1@test.com - user10@test.com : User123!")
        
        print("\n💡 TIPS PARA PROBAR FILTROS:")
        print("   • Eventos en diferentes categorías (Conciertos, Deportes, Arte, etc.)")
        print("   • Eventos con diferentes rangos de precios")
        print("   • Eventos en diferentes fechas (próximos, lejanos, hoy)")
        print("   • Eventos con diferentes capacidades y venues")
        print("   • Tickets con descuentos (Early Bird)")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL SEEDING: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
