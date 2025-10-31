# -*- coding: utf-8 -*-
"""
Script para verificar eventos en la base de datos
"""

from app.core.database import SessionLocal
from app.models import Event, EventCategory, TicketType, User, Role
from app.models.event import EventStatus

def check_events():
    """Verificar eventos en la base de datos"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 80)
        print("🔍 VERIFICANDO DATOS EN LA BASE DE DATOS")
        print("=" * 80 + "\n")
        
        # Verificar usuarios organizadores
        print("👥 ORGANIZADORES:")
        organizer_role = db.query(Role).filter(Role.name == "Organizer").first()
        if organizer_role:
            organizers = db.query(User).join(User.roles).filter(Role.name == "Organizer").all()
            print(f"   ✅ {len(organizers)} organizadores encontrados")
            for org in organizers[:3]:  # Mostrar solo los primeros 3
                print(f"      - {org.email}")
            if len(organizers) > 3:
                print(f"      ... y {len(organizers) - 3} más")
        else:
            print("   ❌ Rol 'Organizer' no encontrado")
        
        # Verificar categorías
        print("\n📁 CATEGORÍAS:")
        categories = db.query(EventCategory).filter(EventCategory.is_active == True).all()
        print(f"   ✅ {len(categories)} categorías activas")
        for cat in categories[:5]:
            print(f"      - {cat.name} ({cat.slug})")
        if len(categories) > 5:
            print(f"      ... y {len(categories) - 5} más")
        
        # Verificar eventos
        print("\n🎫 EVENTOS:")
        total_events = db.query(Event).count()
        published_events = db.query(Event).filter(Event.status == EventStatus.PUBLISHED).count()
        draft_events = db.query(Event).filter(Event.status == EventStatus.DRAFT).count()
        
        print(f"   📊 Total: {total_events} eventos")
        print(f"   ✅ Publicados: {published_events} eventos")
        print(f"   📝 Borradores: {draft_events} eventos")
        
        if total_events > 0:
            print("\n   🎯 Eventos recientes:")
            recent_events = db.query(Event).filter(
                Event.status == EventStatus.PUBLISHED
            ).order_by(Event.startDate.asc()).limit(5).all()
            
            for event in recent_events:
                ticket_count = len(event.ticket_types)
                date_str = event.startDate.strftime("%d/%m/%Y")
                category_name = event.category.name if event.category else "Sin categoría"
                print(f"      • {event.title}")
                print(f"        📅 {date_str} | 📍 {event.venue} | 🏷️ {category_name}")
                print(f"        🎫 {ticket_count} tipos de tickets | 👥 {event.totalCapacity} capacidad")
        else:
            print("\n   ⚠️  No hay eventos en la base de datos")
            print("   💡 Ejecuta: python seed_diverse_events.py")
        
        # Verificar tipos de tickets
        print("\n🎟️  TIPOS DE TICKETS:")
        ticket_types = db.query(TicketType).all()
        print(f"   📊 Total: {len(ticket_types)} tipos de tickets")
        
        if ticket_types:
            # Calcular precios
            prices = [tt.price for tt in ticket_types]
            free_tickets = len([p for p in prices if p == 0])
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            print(f"   💰 Rango de precios: S/{min_price:.2f} - S/{max_price:.2f}")
            print(f"   📊 Precio promedio: S/{avg_price:.2f}")
            print(f"   🆓 Tickets gratuitos: {free_tickets}")
        
        # Verificar ubicaciones
        print("\n📍 UBICACIONES (VENUES):")
        venues = db.query(Event.venue).distinct().all()
        print(f"   📊 Total: {len(venues)} ubicaciones únicas")
        for (venue,) in venues[:10]:
            print(f"      - {venue}")
        if len(venues) > 10:
            print(f"      ... y {len(venues) - 10} más")
        
        print("\n" + "=" * 80)
        
        if total_events == 0:
            print("⚠️  BASE DE DATOS VACÍA")
            print("\n💡 PASOS RECOMENDADOS:")
            print("   1. Ejecutar: python seed_initial_data.py")
            print("   2. Ejecutar: python seed_diverse_events.py")
        else:
            print("✅ BASE DE DATOS CON DATOS")
            print(f"\n📊 RESUMEN:")
            print(f"   • {len(organizers) if organizer_role else 0} organizadores")
            print(f"   • {len(categories)} categorías")
            print(f"   • {total_events} eventos ({published_events} publicados)")
            print(f"   • {len(ticket_types)} tipos de tickets")
            print(f"   • {len(venues)} ubicaciones")
        
        print("=" * 80 + "\n")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.close()


if __name__ == "__main__":
    check_events()
