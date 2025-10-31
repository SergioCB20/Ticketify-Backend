# -*- coding: utf-8 -*-
"""
Script para verificar el estado actual de la base de datos
Muestra estadísticas y resumen de datos
"""

from app.core.database import SessionLocal
from app.models import (
    User, Event, EventCategory, TicketType, Role, Permission,
    Ticket, Payment, MarketplaceListing, Notification,
    EventStatus
)
from sqlalchemy import func
from datetime import datetime

def get_database_stats():
    """Obtener estadísticas de la base de datos"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("=" * 70)
        print()
        
        # === ESTADÍSTICAS GENERALES ===
        print("📈 RESUMEN GENERAL")
        print("-" * 70)
        
        stats = {
            "Usuarios": db.query(User).count(),
            "Roles": db.query(Role).count(),
            "Permisos": db.query(Permission).count(),
            "Categorías": db.query(EventCategory).count(),
            "Eventos": db.query(Event).count(),
            "Tipos de Tickets": db.query(TicketType).count(),
            "Tickets Vendidos": db.query(Ticket).count(),
            "Pagos": db.query(Payment).count(),
            "Listings Marketplace": db.query(MarketplaceListing).count(),
            "Notificaciones": db.query(Notification).count(),
        }
        
        for key, value in stats.items():
            print(f"   {key:.<25} {value:>5}")
        
        # === USUARIOS ===
        print("\n👥 USUARIOS")
        print("-" * 70)
        
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.isActive == True).count()
        inactive_users = total_users - active_users
        
        print(f"   Total: {total_users}")
        print(f"   Activos: {active_users}")
        print(f"   Inactivos: {inactive_users}")
        
        # Usuarios por rol
        organizers = db.query(User).join(User.roles).filter(Role.name == "Organizer").count()
        attendees = db.query(User).join(User.roles).filter(Role.name == "Attendee").count()
        
        print(f"\n   Por rol:")
        print(f"     - Organizadores: {organizers}")
        print(f"     - Asistentes: {attendees}")
        
        # === CATEGORÍAS ===
        print("\n📂 CATEGORÍAS")
        print("-" * 70)
        
        categories = db.query(
            EventCategory.name,
            func.count(Event.id).label('event_count')
        ).outerjoin(Event).group_by(EventCategory.name).order_by(EventCategory.name).all()
        
        for category in categories:
            icon = "🎯"
            if "Concert" in category.name or "Music" in category.name:
                icon = "🎵"
            elif "Deport" in category.name or "Sport" in category.name:
                icon = "⚽"
            elif "Arte" in category.name or "Art" in category.name:
                icon = "🎨"
            elif "Festival" in category.name:
                icon = "🎉"
            
            print(f"   {icon} {category.name:.<30} {category.event_count:>3} eventos")
        
        # === EVENTOS ===
        print("\n🎭 EVENTOS")
        print("-" * 70)
        
        total_events = db.query(Event).count()
        print(f"   Total: {total_events}")
        
        # Por estado
        print(f"\n   Por estado:")
        for status in EventStatus:
            count = db.query(Event).filter(Event.status == status).count()
            if count > 0:
                print(f"     - {status.value}: {count}")
        
        # Por fecha
        today = datetime.now()
        future_events = db.query(Event).filter(Event.startDate > today).count()
        past_events = db.query(Event).filter(Event.startDate <= today).count()
        
        print(f"\n   Por fecha:")
        print(f"     - Futuros: {future_events}")
        print(f"     - Pasados: {past_events}")
        
        # Próximos eventos
        upcoming = db.query(Event).filter(
            Event.startDate > today,
            Event.status == EventStatus.PUBLISHED
        ).order_by(Event.startDate).limit(5).all()
        
        if upcoming:
            print(f"\n   📅 Próximos 5 eventos:")
            for event in upcoming:
                days_until = (event.startDate - today).days
                print(f"     - {event.title[:40]:.<42} en {days_until:>2} días")
        
        # === TICKETS ===
        print("\n🎫 TICKETS")
        print("-" * 70)
        
        total_ticket_types = db.query(TicketType).count()
        total_tickets_sold = db.query(Ticket).count()
        
        print(f"   Tipos de tickets: {total_ticket_types}")
        print(f"   Tickets vendidos: {total_tickets_sold}")
        
        # Capacidad total vs vendida
        total_capacity = db.query(func.sum(TicketType.quantity_available)).scalar() or 0
        total_sold = db.query(func.sum(TicketType.sold_quantity)).scalar() or 0
        
        if total_capacity > 0:
            percentage = (total_sold / total_capacity) * 100
            print(f"\n   Capacidad total: {total_capacity:,}")
            print(f"   Vendidos: {total_sold:,}")
            print(f"   Disponibles: {total_capacity - total_sold:,}")
            print(f"   Ocupación: {percentage:.1f}%")
        
        # Rangos de precio
        min_price = db.query(func.min(TicketType.price)).scalar()
        max_price = db.query(func.max(TicketType.price)).scalar()
        avg_price = db.query(func.avg(TicketType.price)).scalar()
        
        if min_price is not None:
            print(f"\n   Precios:")
            print(f"     - Mínimo: S/ {float(min_price):.2f}")
            print(f"     - Máximo: S/ {float(max_price):.2f}")
            print(f"     - Promedio: S/ {float(avg_price):.2f}")
        
        # === MARKETPLACE ===
        print("\n🏪 MARKETPLACE")
        print("-" * 70)
        
        total_listings = db.query(MarketplaceListing).count()
        active_listings = db.query(MarketplaceListing).filter(
            MarketplaceListing.status == "ACTIVE"
        ).count()
        sold_listings = db.query(MarketplaceListing).filter(
            MarketplaceListing.status == "SOLD"
        ).count()
        
        print(f"   Total listings: {total_listings}")
        print(f"   Activos: {active_listings}")
        print(f"   Vendidos: {sold_listings}")
        
        # === SISTEMA ===
        print("\n⚙️  SISTEMA")
        print("-" * 70)
        
        print(f"   Roles configurados: {db.query(Role).count()}")
        print(f"   Permisos disponibles: {db.query(Permission).count()}")
        print(f"   Notificaciones: {db.query(Notification).count()}")
        
        # Notificaciones no leídas
        unread = db.query(Notification).filter(Notification.is_read == False).count()
        if unread > 0:
            print(f"   Notificaciones sin leer: {unread}")
        
        print("\n" + "=" * 70)
        print("✅ Análisis completado")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al obtener estadísticas: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def list_sample_data():
    """Listar algunos datos de ejemplo"""
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 70)
        print("📋 DATOS DE EJEMPLO")
        print("=" * 70)
        
        # === USUARIOS ===
        print("\n👤 Usuarios de ejemplo (primeros 5):")
        print("-" * 70)
        users = db.query(User).limit(5).all()
        for user in users:
            roles = ", ".join([role.name for role in user.roles])
            print(f"   {user.email:.<35} ({roles})")
        
        # === EVENTOS ===
        print("\n🎭 Eventos de ejemplo (primeros 10):")
        print("-" * 70)
        events = db.query(Event).limit(10).all()
        for event in events:
            category_name = event.category.name if event.category else "Sin categoría"
            status_icon = "✅" if event.status == EventStatus.PUBLISHED else "⏸️"
            print(f"   {status_icon} {event.title[:45]:.<47} [{category_name}]")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al listar datos: {e}")
    finally:
        db.close()


def main():
    """Función principal"""
    print("\n🔍 VERIFICADOR DE BASE DE DATOS - TICKETIFY")
    
    get_database_stats()
    
    print("\n")
    response = input("¿Deseas ver datos de ejemplo? (s/n): ")
    
    if response.lower() in ['s', 'si', 'y', 'yes']:
        list_sample_data()
    
    print("\n✨ ¡Listo!")


if __name__ == "__main__":
    main()
