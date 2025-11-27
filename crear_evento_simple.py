"""
Script simple para crear un evento de prueba para un organizador específico por email
Uso: python crear_evento_simple.py email@organizador.com
"""
import sys
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.event import Event, EventStatus
from app.models.ticket_type import TicketType
from app.models.event_category import EventCategory
from app.models.role import Role


def crear_evento_para_email(email: str):
    """Crea un evento de prueba para un organizador específico"""
    db = SessionLocal()
    
    try:
        # Buscar usuario por email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ No se encontró usuario con email: {email}")
            return
        
        # Verificar que sea organizador
        organizer_role = db.query(Role).filter(Role.name == UserRole.ORGANIZER).first()
        if not organizer_role or organizer_role not in user.roles:
            print(f"⚠️  El usuario {email} no tiene rol de ORGANIZER")
            agregar = input("¿Deseas agregarlo como organizador? (s/N): ").strip().lower()
            if agregar == 's' and organizer_role:
                user.roles.append(organizer_role)
                db.commit()
                print("✅ Rol de organizador agregado")
            else:
                return
        
        print(f"\n📋 Creando evento para: {user.firstName} {user.lastName} ({email})")
        
        # Obtener primera categoría activa
        category = db.query(EventCategory).filter(EventCategory.is_active == True).first()
        
        # Crear evento
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        event = Event(
            title=f"Evento de Prueba {timestamp}",
            description="Evento creado automáticamente para pruebas",
            startDate=datetime.now() + timedelta(days=15),
            endDate=datetime.now() + timedelta(days=15, hours=3),
            venue="Centro de Convenciones, Lima",
            totalCapacity=500,
            status=EventStatus.PUBLISHED,
            organizer_id=user.id,
            category_id=category.id if category else None
        )
        
        db.add(event)
        db.flush()
        
        print(f"✅ Evento creado: {event.title}")
        print(f"   ID: {event.id}")
        print(f"   Fecha: {event.startDate.strftime('%Y-%m-%d %H:%M')}")
        
        # Crear 3 tipos de tickets básicos
        tickets_data = [
            {"name": "General", "price": "40.00", "quantity": 300},
            {"name": "Preferencial", "price": "80.00", "quantity": 150},
            {"name": "VIP", "price": "120.00", "quantity": 50}
        ]
        
        print("\n🎫 Creando tipos de tickets...")
        for tt_data in tickets_data:
            ticket_type = TicketType(
                event_id=event.id,
                name=tt_data["name"],
                description=f"Entrada {tt_data['name']} para el evento",
                price=Decimal(tt_data["price"]),
                original_price=Decimal(tt_data["price"]),
                quantity_available=tt_data["quantity"],
                sold_quantity=0,
                min_purchase=1,
                max_purchase=8,
                is_active=True
            )
            db.add(ticket_type)
            print(f"   ✓ {tt_data['name']}: S/ {tt_data['price']} ({tt_data['quantity']} disponibles)")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("✨ EVENTO CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"Organizador: {user.firstName} {user.lastName}")
        print(f"Email: {email}")
        print(f"Evento ID: {event.id}")
        print(f"Título: {event.title}")
        print(f"Estado: {event.status.value}")
        print(f"Tipos de tickets: {len(tickets_data)}")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n❌ Uso: python crear_evento_simple.py email@organizador.com")
        print("\nEjemplo:")
        print("   python crear_evento_simple.py organizador@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    crear_evento_para_email(email)
