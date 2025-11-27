"""
Script para crear eventos de prueba en Ticketify
Crea un evento completo con tipos de tickets para un organizador específico
Uso: python crear_evento_organizador.py
"""
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

# Configurar el path para importar los módulos de la app
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.event import Event, EventStatus
from app.models.ticket_type import TicketType
from app.models.event_category import EventCategory
from app.models.role import Role

def mostrar_usuarios_organizadores(db):
    """Muestra todos los usuarios que tienen el rol de organizador"""
    print("\n=== USUARIOS ORGANIZADORES ===")
    
    # Buscar el rol de organizador
    organizer_role = db.query(Role).filter(Role.name == UserRole.ORGANIZER).first()
    
    if not organizer_role:
        print("❌ No existe el rol ORGANIZER en la base de datos")
        return []
    
    # Obtener usuarios con rol organizador
    organizers = db.query(User).join(User.roles).filter(Role.name == UserRole.ORGANIZER).all()
    
    if not organizers:
        print("❌ No hay usuarios con rol ORGANIZER")
        print("\n💡 Tip: Crea un usuario organizador desde la aplicación o modifica un usuario existente")
        return []
    
    for i, user in enumerate(organizers, 1):
        print(f"{i}. {user.email} - {user.firstName} {user.lastName}")
        print(f"   ID: {user.id}")
        print(f"   Activo: {'Sí' if user.isActive else 'No'}")
        if user.organized_events:
            print(f"   Eventos creados: {len(user.organized_events)}")
        print()
    
    return organizers


def mostrar_categorias(db):
    """Muestra todas las categorías disponibles"""
    print("\n=== CATEGORÍAS DISPONIBLES ===")
    categories = db.query(EventCategory).filter(EventCategory.is_active == True).all()
    
    if not categories:
        print("⚠️  No hay categorías activas en la base de datos")
        return []
    
    for i, cat in enumerate(categories, 1):
        print(f"{i}. {cat.name} ({cat.slug})")
        if cat.description:
            print(f"   {cat.description}")
        print()
    
    return categories


def crear_evento_interactivo():
    """
    Crea un evento de prueba de forma interactiva
    """
    db = SessionLocal()
    
    try:
        print("\n🎉 CREADOR DE EVENTOS - TICKETIFY")
        print("=" * 60)
        
        # 1. Seleccionar organizador
        organizers = mostrar_usuarios_organizadores(db)
        
        if not organizers:
            print("\n❌ No se puede continuar sin organizadores")
            return
        
        user_choice = input(f"\n📝 Selecciona el organizador (1-{len(organizers)}): ")
        try:
            user_index = int(user_choice) - 1
            if user_index < 0 or user_index >= len(organizers):
                print("❌ Selección inválida")
                return
            selected_user = organizers[user_index]
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            return
        
        print(f"✅ Organizador seleccionado: {selected_user.firstName} {selected_user.lastName}")
        
        # 2. Información del evento
        print("\n" + "=" * 60)
        print("📋 INFORMACIÓN DEL EVENTO")
        print("=" * 60)
        
        title = input("\n📌 Título del evento: ").strip()
        if not title:
            print("❌ El título no puede estar vacío")
            return
        
        description = input("📝 Descripción: ").strip()
        
        venue = input("📍 Lugar (ej: Estadio Nacional, Lima): ").strip()
        if not venue:
            print("❌ El lugar no puede estar vacío")
            return
        
        # Fechas
        print("\n📅 FECHAS DEL EVENTO")
        dias_adelante = input("¿En cuántos días será el evento? (default: 30): ").strip()
        dias_adelante = int(dias_adelante) if dias_adelante else 30
        
        duracion_horas = input("¿Cuántas horas durará? (default: 4): ").strip()
        duracion_horas = int(duracion_horas) if duracion_horas else 4
        
        start_date = datetime.now() + timedelta(days=dias_adelante)
        end_date = start_date + timedelta(hours=duracion_horas)
        
        print(f"   Inicio: {start_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Fin: {end_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Capacidad
        capacidad = input("\n👥 Capacidad total del evento (default: 1000): ").strip()
        total_capacity = int(capacidad) if capacidad else 1000
        
        # 3. Seleccionar categoría
        categories = mostrar_categorias(db)
        category = None
        
        if categories:
            cat_choice = input(f"🏷️  Selecciona una categoría (1-{len(categories)}, o Enter para omitir): ").strip()
            if cat_choice:
                try:
                    cat_index = int(cat_choice) - 1
                    if 0 <= cat_index < len(categories):
                        category = categories[cat_index]
                        print(f"✅ Categoría: {category.name}")
                except ValueError:
                    print("⚠️  Categoría no válida, se omitirá")
        
        # 4. Crear el evento
        print("\n" + "=" * 60)
        print("🎬 CREANDO EVENTO...")
        print("=" * 60)
        
        event = Event(
            title=title,
            description=description if description else None,
            startDate=start_date,
            endDate=end_date,
            venue=venue,
            totalCapacity=total_capacity,
            status=EventStatus.PUBLISHED,  # Publicado por defecto para pruebas
            organizer_id=selected_user.id,
            category_id=category.id if category else None
        )
        
        db.add(event)
        db.flush()  # Para obtener el ID del evento
        
        print(f"✅ Evento '{title}' creado con ID: {event.id}")
        
        # 5. Crear tipos de tickets
        print("\n" + "=" * 60)
        print("🎫 TIPOS DE TICKETS")
        print("=" * 60)
        
        crear_tickets = input("\n¿Deseas crear tipos de tickets ahora? (s/N): ").strip().lower()
        
        if crear_tickets == 's':
            num_tipos = input("¿Cuántos tipos de tickets? (default: 3): ").strip()
            num_tipos = int(num_tipos) if num_tipos else 3
            
            tickets_predefinidos = [
                {"name": "General", "price": 50.00, "quantity": int(total_capacity * 0.6)},
                {"name": "VIP", "price": 150.00, "quantity": int(total_capacity * 0.3)},
                {"name": "Platea", "price": 100.00, "quantity": int(total_capacity * 0.1)}
            ]
            
            for i in range(num_tipos):
                print(f"\n--- Tipo de Ticket #{i + 1} ---")
                
                # Usar predefinidos si existen
                if i < len(tickets_predefinidos):
                    preset = tickets_predefinidos[i]
                    nombre = input(f"Nombre (default: {preset['name']}): ").strip() or preset['name']
                    precio = input(f"Precio en soles (default: {preset['price']}): ").strip()
                    precio = Decimal(precio) if precio else Decimal(str(preset['price']))
                    cantidad = input(f"Cantidad disponible (default: {preset['quantity']}): ").strip()
                    cantidad = int(cantidad) if cantidad else preset['quantity']
                else:
                    nombre = input("Nombre: ").strip()
                    if not nombre:
                        print("⚠️  Omitiendo este tipo de ticket")
                        continue
                    precio = Decimal(input("Precio en soles: ").strip())
                    cantidad = int(input("Cantidad disponible: ").strip())
                
                desc = input(f"Descripción (opcional): ").strip()
                
                ticket_type = TicketType(
                    event_id=event.id,
                    name=nombre,
                    description=desc if desc else None,
                    price=precio,
                    original_price=precio,  # Mismo precio inicial
                    quantity_available=cantidad,
                    sold_quantity=0,
                    min_purchase=1,
                    max_purchase=10,
                    is_active=True
                )
                
                db.add(ticket_type)
                print(f"✅ Tipo de ticket '{nombre}' creado (S/ {precio}, {cantidad} disponibles)")
        
        # 6. Commit final
        db.commit()
        
        # 7. Resumen
        print("\n" + "=" * 60)
        print("✨ EVENTO CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\n📋 RESUMEN DEL EVENTO")
        print(f"{'─' * 60}")
        print(f"ID: {event.id}")
        print(f"Título: {event.title}")
        print(f"Descripción: {event.description or '(sin descripción)'}")
        print(f"Organizador: {selected_user.firstName} {selected_user.lastName}")
        print(f"Email Organizador: {selected_user.email}")
        print(f"Lugar: {event.venue}")
        print(f"Fecha Inicio: {event.startDate.strftime('%Y-%m-%d %H:%M')}")
        print(f"Fecha Fin: {event.endDate.strftime('%Y-%m-%d %H:%M')}")
        print(f"Capacidad: {event.totalCapacity} personas")
        print(f"Estado: {event.status.value}")
        if category:
            print(f"Categoría: {category.name}")
        
        # Mostrar tipos de tickets creados
        ticket_types = db.query(TicketType).filter(TicketType.event_id == event.id).all()
        if ticket_types:
            print(f"\n🎫 TIPOS DE TICKETS ({len(ticket_types)}):")
            for tt in ticket_types:
                print(f"   • {tt.name}: S/ {tt.price} - {tt.quantity_available} disponibles")
        
        print(f"\n{'─' * 60}")
        print(f"✅ Puedes ver este evento en la aplicación iniciando sesión como:")
        print(f"   📧 {selected_user.email}")
        print(f"{'=' * 60}\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


def crear_evento_rapido():
    """
    Crea un evento de prueba rápido con valores predefinidos
    """
    db = SessionLocal()
    
    try:
        print("\n🚀 CREACIÓN RÁPIDA DE EVENTO")
        print("=" * 60)
        
        # Obtener primer organizador
        organizer_role = db.query(Role).filter(Role.name == UserRole.ORGANIZER).first()
        if not organizer_role:
            print("❌ No existe el rol ORGANIZER")
            return
        
        organizer = db.query(User).join(User.roles).filter(Role.name == UserRole.ORGANIZER).first()
        
        if not organizer:
            print("❌ No hay usuarios organizadores en la base de datos")
            return
        
        print(f"Organizador: {organizer.email}")
        
        # Obtener primera categoría
        category = db.query(EventCategory).filter(EventCategory.is_active == True).first()
        
        # Crear evento
        event = Event(
            title=f"Concierto Rock 2025 - {datetime.now().strftime('%H:%M:%S')}",
            description="Evento de prueba creado automáticamente",
            startDate=datetime.now() + timedelta(days=30),
            endDate=datetime.now() + timedelta(days=30, hours=4),
            venue="Estadio Nacional, Lima",
            totalCapacity=1000,
            status=EventStatus.PUBLISHED,
            organizer_id=organizer.id,
            category_id=category.id if category else None
        )
        
        db.add(event)
        db.flush()
        
        # Crear tipos de tickets predefinidos
        ticket_types_data = [
            {"name": "General", "price": "50.00", "quantity": 600},
            {"name": "VIP", "price": "150.00", "quantity": 300},
            {"name": "Platea", "price": "100.00", "quantity": 100}
        ]
        
        for tt_data in ticket_types_data:
            ticket_type = TicketType(
                event_id=event.id,
                name=tt_data["name"],
                description=f"Entrada {tt_data['name']}",
                price=Decimal(tt_data["price"]),
                original_price=Decimal(tt_data["price"]),
                quantity_available=tt_data["quantity"],
                sold_quantity=0,
                min_purchase=1,
                max_purchase=10,
                is_active=True
            )
            db.add(ticket_type)
        
        db.commit()
        
        print(f"\n✅ Evento creado exitosamente!")
        print(f"   ID: {event.id}")
        print(f"   Título: {event.title}")
        print(f"   Organizador: {organizer.email}")
        print(f"   Tipos de tickets: {len(ticket_types_data)}")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎉 CREADOR DE EVENTOS - TICKETIFY")
    print("=" * 60)
    print("\nModos disponibles:")
    print("1. Creación interactiva (personalizada)")
    print("2. Creación rápida (valores predefinidos)")
    print("3. Salir")
    
    opcion = input("\nSelecciona una opción (1-3): ").strip()
    
    if opcion == "1":
        crear_evento_interactivo()
    elif opcion == "2":
        crear_evento_rapido()
    elif opcion == "3":
        print("\n👋 ¡Hasta luego!")
    else:
        print("\n❌ Opción inválida")
