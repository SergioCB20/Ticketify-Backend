"""
Script para poblar la base de datos con datos de prueba
Ejecutar: python -m app.seeds.seed_data
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import (
    User, Event, EventCategory, TicketType, EventStatus,
    Role, Permission
)
import bcrypt
import uuid

def safe_hash_password(password: str) -> str:
    """
    Hash de contraseña usando bcrypt directamente
    """
    # Convertir a bytes y asegurar que no exceda 72 bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncar a 72 bytes de forma segura
        password_bytes = password_bytes[:72]
        print(f"   ⚠️  Contraseña truncada a 72 bytes")
    
    # Generar el hash directamente con bcrypt
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_categories(db: Session):
    """Crear categorías de eventos"""
    print("\n📁 Creando categorías...")
    
    categories = [
        {
            "name": "Conciertos",
            "slug": "conciertos",
            "description": "Eventos musicales y conciertos en vivo",
            "icon": "🎵",
            "color": "#FF6B6B"
        },
        {
            "name": "Deportes",
            "slug": "deportes",
            "description": "Eventos deportivos y competencias",
            "icon": "⚽",
            "color": "#4ECDC4"
        },
        {
            "name": "Teatro",
            "slug": "teatro",
            "description": "Obras de teatro y presentaciones escénicas",
            "icon": "🎭",
            "color": "#95E1D3"
        },
        {
            "name": "Conferencias",
            "slug": "conferencias",
            "description": "Charlas, seminarios y eventos corporativos",
            "icon": "💼",
            "color": "#F38181"
        },
        {
            "name": "Festivales",
            "slug": "festivales",
            "description": "Festivales culturales y gastronómicos",
            "icon": "🎪",
            "color": "#AA96DA"
        }
    ]
    
    created_categories = []
    skipped = 0
    
    for cat_data in categories:
        # Verificar si la categoría ya existe
        existing = db.query(EventCategory).filter_by(name=cat_data["name"]).first()
        if existing:
            created_categories.append(existing)
            print(f"   ⏭️  {cat_data['name']} (ya existe)")
            skipped += 1
            continue
        
        category = EventCategory(
            id=uuid.uuid4(),
            name=cat_data["name"],
            slug=cat_data["slug"],
            description=cat_data["description"],
            icon=cat_data["icon"],
            color=cat_data["color"],
            sort_order=len(created_categories),
            level=0,
            is_active=True,
            is_featured=True
        )
        db.add(category)
        created_categories.append(category)
        print(f"   ✅ {cat_data['name']}")
    
    if len(created_categories) - skipped > 0:
        db.commit()
    
    print(f"   ✨ {len(created_categories) - skipped} categorías creadas, {skipped} ya existían")
    return created_categories


def create_users(db: Session):
    """Crear usuarios de prueba"""
    print("\n👥 Creando usuarios...")
    
    users_data = [
        {
            "email": "admin@ticketify.com",
            "password": "admin123",
            "firstName": "Admin",
            "lastName": "Ticketify",
            "phoneNumber": "+51999888777",
            "documentId": "12345678"
        },
        {
            "email": "organizador@ticketify.com",
            "password": "org123",
            "firstName": "Carlos",
            "lastName": "Promotor",
            "phoneNumber": "+51999777666",
            "documentId": "87654321"
        },
        {
            "email": "usuario@ticketify.com",
            "password": "user123",
            "firstName": "María",
            "lastName": "González",
            "phoneNumber": "+51999666555",
            "documentId": "11223344"
        }
    ]
    
    created_users = []
    skipped = 0
    
    for user_data in users_data:
        try:
            # Verificar si el usuario ya existe
            existing = db.query(User).filter_by(email=user_data["email"]).first()
            if existing:
                created_users.append(existing)
                print(f"   ⏭️  {user_data['email']} (ya existe)")
                skipped += 1
                continue
            
            hashed_password = safe_hash_password(user_data["password"])
            
            user = User(
                id=uuid.uuid4(),
                email=user_data["email"],
                password=hashed_password,
                firstName=user_data["firstName"],
                lastName=user_data["lastName"],
                phoneNumber=user_data["phoneNumber"],
                documentId=user_data["documentId"],
                isActive=True,
                createdAt=datetime.utcnow()
            )
            db.add(user)
            created_users.append(user)
            print(f"   ✅ {user_data['email']} (password: {user_data['password']})")
        except Exception as e:
            print(f"   ❌ Error creando usuario {user_data['email']}: {e}")
            raise
    
    if len(created_users) - skipped > 0:
        db.commit()
    
    print(f"   ✨ {len(created_users) - skipped} usuarios creados, {skipped} ya existían")
    return created_users


def create_events(db: Session, organizer: User, categories: list):
    """Crear eventos de prueba"""
    print("\n🎉 Creando eventos...")
    
    now = datetime.utcnow()
    
    events_data = [
        {
            "title": "Concierto de Rock en Vivo",
            "description": "Una noche inolvidable con las mejores bandas de rock nacional e internacional. ¡No te lo pierdas!",
            "startDate": now + timedelta(days=30),
            "endDate": now + timedelta(days=30, hours=4),
            "venue": "Estadio Nacional - Lima",
            "totalCapacity": 5000,
            "category": categories[0],  # Conciertos
            "multimedia": [
                "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800",
                "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800"
            ]
        },
        {
            "title": "Partido de Fútbol: Clásico Peruano",
            "description": "El clásico más esperado del año. Dos equipos históricos se enfrentan en un partido épico.",
            "startDate": now + timedelta(days=15),
            "endDate": now + timedelta(days=15, hours=2),
            "venue": "Estadio Monumental - Lima",
            "totalCapacity": 8000,
            "category": categories[1],  # Deportes
            "multimedia": [
                "https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=800"
            ]
        },
        {
            "title": "Festival Gastronómico Mistura",
            "description": "El festival gastronómico más grande de Latinoamérica. Sabores de todo el Perú en un solo lugar.",
            "startDate": now + timedelta(days=45),
            "endDate": now + timedelta(days=48),
            "venue": "Costa Verde - Lima",
            "totalCapacity": 10000,
            "category": categories[4],  # Festivales
            "multimedia": [
                "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800"
            ]
        },
        {
            "title": "Obra de Teatro: El Avaro",
            "description": "Clásico de Molière adaptado por el mejor elenco nacional. Una comedia imperdible.",
            "startDate": now + timedelta(days=20),
            "endDate": now + timedelta(days=20, hours=2),
            "venue": "Teatro Municipal - Lima",
            "totalCapacity": 500,
            "category": categories[2],  # Teatro
            "multimedia": [
                "https://images.unsplash.com/photo-1503095396549-807759245b35?w=800"
            ]
        },
        {
            "title": "Tech Summit Lima 2025",
            "description": "La conferencia de tecnología más importante del año. Speakers internacionales, workshops y networking.",
            "startDate": now + timedelta(days=60),
            "endDate": now + timedelta(days=62),
            "venue": "Centro de Convenciones - San Isidro",
            "totalCapacity": 2000,
            "category": categories[3],  # Conferencias
            "multimedia": [
                "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800"
            ]
        },
        {
            "title": "Concierto de Salsa: Los Grandes",
            "description": "Las mejores orquestas de salsa del Perú juntas en un solo escenario.",
            "startDate": now + timedelta(days=10),
            "endDate": now + timedelta(days=10, hours=5),
            "venue": "Arena del Jockey - Surco",
            "totalCapacity": 3000,
            "category": categories[0],  # Conciertos
            "multimedia": [
                "https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?w=800"
            ]
        }
    ]
    
    created_events = []
    for event_data in events_data:
        event = Event(
            id=uuid.uuid4(),
            title=event_data["title"],
            description=event_data["description"],
            startDate=event_data["startDate"],
            endDate=event_data["endDate"],
            venue=event_data["venue"],
            totalCapacity=event_data["totalCapacity"],
            status=EventStatus.PUBLISHED,
            multimedia=event_data["multimedia"],
            organizer_id=organizer.id,
            category_id=event_data["category"].id,
            createdAt=datetime.utcnow()
        )
        db.add(event)
        created_events.append(event)
        print(f"   ✅ {event_data['title']}")
    
    db.commit()
    print(f"   ✨ {len(created_events)} eventos creados")
    return created_events


def create_ticket_types(db: Session, events: list):
    """Crear tipos de tickets para cada evento"""
    print("\n🎫 Creando tipos de tickets...")
    
    ticket_count = 0
    for event in events:
        # Tipos de tickets según capacidad del evento
        if event.totalCapacity >= 5000:
            ticket_types = [
                {"name": "General", "price": 50.00, "quantity": int(event.totalCapacity * 0.6)},
                {"name": "VIP", "price": 150.00, "quantity": int(event.totalCapacity * 0.3)},
                {"name": "Platinum", "price": 300.00, "quantity": int(event.totalCapacity * 0.1)}
            ]
        elif event.totalCapacity >= 1000:
            ticket_types = [
                {"name": "General", "price": 35.00, "quantity": int(event.totalCapacity * 0.7)},
                {"name": "Preferencial", "price": 80.00, "quantity": int(event.totalCapacity * 0.3)}
            ]
        else:
            ticket_types = [
                {"name": "General", "price": 25.00, "quantity": event.totalCapacity}
            ]
        
        for tt_data in ticket_types:
            ticket_type = TicketType(
                id=uuid.uuid4(),
                name=tt_data["name"],
                price=tt_data["price"],
                quantity_available=tt_data["quantity"],
                sold_quantity=0,
                min_purchase=1,
                max_purchase=10,
                is_active=True,
                is_featured=False,
                sort_order=ticket_count,
                event_id=event.id
            )
            db.add(ticket_type)
            ticket_count += 1
    
    db.commit()
    print(f"   ✨ {ticket_count} tipos de tickets creados")


def seed_database():
    """Función principal para poblar la base de datos"""
    print("=" * 70)
    print("🌱 SEEDING DATABASE - Ticketify")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Crear datos (verificando duplicados internamente)
        categories = create_categories(db)
        users = create_users(db)
        events = create_events(db, users[1], categories)  # Organizador
        create_ticket_types(db, events)
        
        print("\n" + "=" * 70)
        print("✅ SEEDING COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        print("\n📝 Credenciales de prueba:")
        print("   Admin: admin@ticketify.com / admin123")
        print("   Organizador: organizador@ticketify.com / org123")
        print("   Usuario: usuario@ticketify.com / user123")
        print("\n🌐 Accede a: http://localhost:8000/docs")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al crear datos: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
