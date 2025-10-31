# -*- coding: utf-8 -*-
"""
Script para crear eventos de prueba con datos variados para testing de filtros
Ejecutar después de seed_initial_data.py
"""

from app.core.database import SessionLocal
from app.models import (
    User, Event, EventCategory, TicketType, Role,
    EventStatus
)
from datetime import datetime, timedelta
from decimal import Decimal
import random

def create_test_users():
    """Crear usuarios organizadores de prueba"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen usuarios de prueba
        existing_user = db.query(User).filter(User.email == "organizador1@test.com").first()
        if existing_user:
            print("⚠️  Los usuarios de prueba ya existen")
            return
        
        # Obtener rol de organizador
        organizer_role = db.query(Role).filter(Role.name == "Organizer").first()
        attendee_role = db.query(Role).filter(Role.name == "Attendee").first()
        
        users = [
            User(
                email="organizador1@test.com",
                password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYf8nE8o8W.",  # password: Test123!
                firstName="Carlos",
                lastName="González",
                phoneNumber="+51987654321",
                documentId="12345678",
                isActive=True,
                roles=[organizer_role, attendee_role]
            ),
            User(
                email="organizador2@test.com",
                password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYf8nE8o8W.",
                firstName="María",
                lastName="Rodriguez",
                phoneNumber="+51987654322",
                documentId="87654321",
                isActive=True,
                roles=[organizer_role, attendee_role]
            ),
            User(
                email="organizador3@test.com",
                password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYf8nE8o8W.",
                firstName="José",
                lastName="Martínez",
                phoneNumber="+51987654323",
                documentId="11223344",
                isActive=True,
                roles=[organizer_role, attendee_role]
            )
        ]
        
        db.add_all(users)
        db.commit()
        
        print("✅ Usuarios organizadores creados:")
        for user in users:
            print(f"   - {user.email} ({user.full_name})")
        
        return users
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear usuarios: {e}")
        return []
    finally:
        db.close()


def create_test_events():
    """Crear eventos de prueba con diferentes características"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen eventos
        existing_event = db.query(Event).first()
        if existing_event:
            print("⚠️  Ya existen eventos, limpiando para recrear...")
            # Opcional: descomentar para limpiar
            # db.query(Event).delete()
            # db.commit()
        
        # Obtener categorías
        categories = {cat.slug: cat for cat in db.query(EventCategory).all()}
        
        # Obtener organizadores
        organizers = db.query(User).filter(User.email.like("%organizador%")).all()
        if not organizers:
            print("❌ No se encontraron organizadores. Ejecuta create_test_users() primero")
            return
        
        # Definir fechas base
        today = datetime.now()
        
        events_data = [
            # CONCIERTOS
            {
                "title": "Festival Rock en Español 2025",
                "description": "El mayor festival de rock en español con bandas internacionales. Tres días de música, arte y cultura con más de 20 artistas.",
                "startDate": today + timedelta(days=30),
                "endDate": today + timedelta(days=32),
                "venue": "Estadio Nacional, Lima",
                "totalCapacity": 15000,
                "status": EventStatus.PUBLISHED,
                "category": "conciertos",
                "multimedia": [
                    "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800",
                    "https://images.unsplash.com/photo-1524368535928-5b5e00ddc76b?w=800"
                ],
                "ticket_types": [
                    {"name": "General", "price": 150.00, "quantity": 10000},
                    {"name": "VIP", "price": 350.00, "quantity": 2000},
                    {"name": "Platinum", "price": 500.00, "quantity": 500}
                ]
            },
            {
                "title": "Noche de Salsa y Bachata",
                "description": "Una noche mágica con los mejores exponentes de la salsa y bachata. Incluye clases de baile gratuitas.",
                "startDate": today + timedelta(days=15),
                "endDate": today + timedelta(days=15),
                "venue": "Club Social Lima, Miraflores",
                "totalCapacity": 500,
                "status": EventStatus.PUBLISHED,
                "category": "conciertos",
                "multimedia": [
                    "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=800"
                ],
                "ticket_types": [
                    {"name": "General", "price": 80.00, "quantity": 400},
                    {"name": "VIP con Mesa", "price": 200.00, "quantity": 100}
                ]
            },
            
            # DEPORTES
            {
                "title": "Maratón Lima 2025",
                "description": "42K por las principales calles de Lima. Incluye categorías: 42K, 21K, 10K y 5K. Camiseta técnica y medalla incluida.",
                "startDate": today + timedelta(days=45),
                "endDate": today + timedelta(days=45),
                "venue": "Parque Kennedy - Circuito Costa Verde, Lima",
                "totalCapacity": 5000,
                "status": EventStatus.PUBLISHED,
                "category": "deportes",
                "multimedia": [
                    "https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=800"
                ],
                "ticket_types": [
                    {"name": "42K Marathon", "price": 120.00, "quantity": 1000},
                    {"name": "21K Half Marathon", "price": 80.00, "quantity": 1500},
                    {"name": "10K", "price": 50.00, "quantity": 1500},
                    {"name": "5K", "price": 35.00, "quantity": 1000}
                ]
            },
            {
                "title": "Torneo de Fútbol 7 Empresarial",
                "description": "Torneo relámpago de fútbol 7 para equipos empresariales. Premios para los tres primeros lugares.",
                "startDate": today + timedelta(days=20),
                "endDate": today + timedelta(days=21),
                "venue": "Complejo Deportivo La Videna, San Luis",
                "totalCapacity": 200,
                "status": EventStatus.PUBLISHED,
                "category": "deportes",
                "multimedia": [
                    "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800"
                ],
                "ticket_types": [
                    {"name": "Equipo Completo (7 jugadores)", "price": 350.00, "quantity": 20},
                    {"name": "Jugador Individual", "price": 50.00, "quantity": 60}
                ]
            },
            
            # ARTE & CULTURA
            {
                "title": "Exposición de Arte Contemporáneo Peruano",
                "description": "Muestra colectiva de 30 artistas peruanos contemporáneos. Incluye pinturas, esculturas y arte digital.",
                "startDate": today + timedelta(days=10),
                "endDate": today + timedelta(days=40),
                "venue": "Museo de Arte Contemporáneo, Barranco",
                "totalCapacity": 3000,
                "status": EventStatus.PUBLISHED,
                "category": "arte-cultura",
                "multimedia": [
                    "https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=800"
                ],
                "ticket_types": [
                    {"name": "Entrada General", "price": 25.00, "quantity": 2500},
                    {"name": "Estudiantes", "price": 15.00, "quantity": 300},
                    {"name": "Adultos Mayores", "price": 15.00, "quantity": 200}
                ]
            },
            {
                "title": "Festival Internacional de Teatro",
                "description": "10 días de teatro con compañías nacionales e internacionales. Más de 50 presentaciones.",
                "startDate": today + timedelta(days=35),
                "endDate": today + timedelta(days=44),
                "venue": "Teatro Municipal de Lima, Centro",
                "totalCapacity": 8000,
                "status": EventStatus.PUBLISHED,
                "category": "arte-cultura",
                "multimedia": [
                    "https://images.unsplash.com/photo-1503095396549-807759245b35?w=800"
                ],
                "ticket_types": [
                    {"name": "Pase Completo", "price": 450.00, "quantity": 500},
                    {"name": "Pase 5 Obras", "price": 250.00, "quantity": 1000},
                    {"name": "Entrada Individual", "price": 60.00, "quantity": 6500}
                ]
            },
            
            # FESTIVALES
            {
                "title": "Mistura - Festival Gastronómico",
                "description": "El festival gastronómico más importante de Latinoamérica. Más de 100 restaurantes y chefs participantes.",
                "startDate": today + timedelta(days=50),
                "endDate": today + timedelta(days=59),
                "venue": "Costa Verde, Magdalena",
                "totalCapacity": 50000,
                "status": EventStatus.PUBLISHED,
                "category": "festivales",
                "multimedia": [
                    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800"
                ],
                "ticket_types": [
                    {"name": "Entrada Diaria", "price": 45.00, "quantity": 40000},
                    {"name": "Pase 3 Días", "price": 120.00, "quantity": 5000},
                    {"name": "Pase VIP Semana", "price": 400.00, "quantity": 1000}
                ]
            },
            {
                "title": "Festival de Cerveza Artesanal",
                "description": "Más de 50 cervecerías artesanales nacionales e internacionales. Food trucks y música en vivo.",
                "startDate": today + timedelta(days=25),
                "endDate": today + timedelta(days=27),
                "venue": "Parque de la Exposición, Lima Centro",
                "totalCapacity": 8000,
                "status": EventStatus.PUBLISHED,
                "category": "festivales",
                "multimedia": [
                    "https://images.unsplash.com/photo-1513309914637-65c20a5962e1?w=800"
                ],
                "ticket_types": [
                    {"name": "Entrada General", "price": 60.00, "quantity": 6000},
                    {"name": "VIP con Degustación", "price": 150.00, "quantity": 1000}
                ]
            },
            
            # COMIDAS & BEBIDAS
            {
                "title": "Cata de Vinos Orgánicos",
                "description": "Experiencia exclusiva de cata de vinos orgánicos con sommelier profesional. Incluye maridaje.",
                "startDate": today + timedelta(days=18),
                "endDate": today + timedelta(days=18),
                "venue": "Restaurant Central, Barranco",
                "totalCapacity": 40,
                "status": EventStatus.PUBLISHED,
                "category": "comidas-bebidas",
                "multimedia": [
                    "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?w=800"
                ],
                "ticket_types": [
                    {"name": "Experiencia Completa", "price": 280.00, "quantity": 40}
                ]
            },
            
            # CURSOS Y TALLERES
            {
                "title": "Taller de Fotografía Profesional",
                "description": "Curso intensivo de 3 días sobre fotografía profesional. Teoría y práctica con equipos profesionales.",
                "startDate": today + timedelta(days=22),
                "endDate": today + timedelta(days=24),
                "venue": "Centro Cultural PUCP, San Miguel",
                "totalCapacity": 25,
                "status": EventStatus.PUBLISHED,
                "category": "cursos-talleres",
                "multimedia": [
                    "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800"
                ],
                "ticket_types": [
                    {"name": "Curso Completo", "price": 450.00, "quantity": 25}
                ]
            },
            {
                "title": "Bootcamp de Programación Web",
                "description": "Bootcamp intensivo de desarrollo web full-stack. 8 semanas de lunes a viernes.",
                "startDate": today + timedelta(days=60),
                "endDate": today + timedelta(days=116),
                "venue": "Laboratoria, San Isidro",
                "totalCapacity": 30,
                "status": EventStatus.PUBLISHED,
                "category": "cursos-talleres",
                "multimedia": [
                    "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800"
                ],
                "ticket_types": [
                    {"name": "Bootcamp Completo", "price": 3500.00, "quantity": 30}
                ]
            },
            
            # ENTRETENIMIENTO
            {
                "title": "Stand Up Comedy Night",
                "description": "Noche de comedia con los mejores comediantes peruanos. Dos shows: 8pm y 10pm.",
                "startDate": today + timedelta(days=12),
                "endDate": today + timedelta(days=12),
                "venue": "Teatro Canout, Miraflores",
                "totalCapacity": 300,
                "status": EventStatus.PUBLISHED,
                "category": "entretenimiento",
                "multimedia": [
                    "https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800"
                ],
                "ticket_types": [
                    {"name": "Show 8pm", "price": 70.00, "quantity": 150},
                    {"name": "Show 10pm", "price": 70.00, "quantity": 150}
                ]
            },
            {
                "title": "Circo Contemporáneo",
                "description": "Espectáculo de circo contemporáneo con acróbatas internacionales y efectos visuales.",
                "startDate": today + timedelta(days=40),
                "endDate": today + timedelta(days=47),
                "venue": "Carpa del Circo, Jockey Plaza",
                "totalCapacity": 2000,
                "status": EventStatus.PUBLISHED,
                "category": "entretenimiento",
                "multimedia": [
                    "https://images.unsplash.com/photo-1543157145-f78c636d023d?w=800"
                ],
                "ticket_types": [
                    {"name": "Platea", "price": 120.00, "quantity": 800},
                    {"name": "Palco", "price": 180.00, "quantity": 400},
                    {"name": "VIP", "price": 250.00, "quantity": 200}
                ]
            },
            
            # CINE
            {
                "title": "Festival de Cine Europeo",
                "description": "Muestra de las mejores películas europeas del año. 15 películas en 5 días.",
                "startDate": today + timedelta(days=28),
                "endDate": today + timedelta(days=32),
                "venue": "Cineplanet Alcázar, Miraflores",
                "totalCapacity": 1500,
                "status": EventStatus.PUBLISHED,
                "category": "cine",
                "multimedia": [
                    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800"
                ],
                "ticket_types": [
                    {"name": "Pase Festival", "price": 180.00, "quantity": 300},
                    {"name": "Entrada Individual", "price": 25.00, "quantity": 1200}
                ]
            },
            
            # AYUDA SOCIAL
            {
                "title": "Concierto Benéfico por la Educación",
                "description": "Concierto benéfico para recaudar fondos para escuelas rurales. Todo lo recaudado se dona.",
                "startDate": today + timedelta(days=55),
                "endDate": today + timedelta(days=55),
                "venue": "Gran Teatro Nacional, San Borja",
                "totalCapacity": 1500,
                "status": EventStatus.PUBLISHED,
                "category": "ayuda-social",
                "multimedia": [
                    "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800"
                ],
                "ticket_types": [
                    {"name": "Entrada Solidaria", "price": 50.00, "quantity": 1000},
                    {"name": "Donación Especial", "price": 150.00, "quantity": 500}
                ]
            },
            
            # EVENTOS PASADOS (para testing de filtros de fecha)
            {
                "title": "Concierto de Año Nuevo 2025 (PASADO)",
                "description": "Gran concierto sinfónico de año nuevo.",
                "startDate": today - timedelta(days=300),
                "endDate": today - timedelta(days=300),
                "venue": "Auditorio Nacional, San Borja",
                "totalCapacity": 800,
                "status": EventStatus.COMPLETED,
                "category": "conciertos",
                "multimedia": [],
                "ticket_types": [
                    {"name": "General", "price": 100.00, "quantity": 800}
                ]
            },
            
            # EVENTOS PRÓXIMOS (diferentes rangos de precio)
            {
                "title": "Evento Gratuito: Clase de Yoga en el Parque",
                "description": "Clase gratuita de yoga al aire libre. Solo necesitas traer tu mat.",
                "startDate": today + timedelta(days=5),
                "endDate": today + timedelta(days=5),
                "venue": "Parque El Olivar, San Isidro",
                "totalCapacity": 100,
                "status": EventStatus.PUBLISHED,
                "category": "deportes",
                "multimedia": [
                    "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800"
                ],
                "ticket_types": [
                    {"name": "Entrada Gratuita", "price": 0.00, "quantity": 100}
                ]
            },
            {
                "title": "Concierto Sinfónico Premium",
                "description": "Concierto exclusivo de la Sinfónica Nacional con director invitado internacional.",
                "startDate": today + timedelta(days=70),
                "endDate": today + timedelta(days=70),
                "venue": "Gran Teatro Nacional, San Borja",
                "totalCapacity": 1200,
                "status": EventStatus.PUBLISHED,
                "category": "conciertos",
                "multimedia": [
                    "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800"
                ],
                "ticket_types": [
                    {"name": "Platinum", "price": 800.00, "quantity": 100},
                    {"name": "Gold", "price": 500.00, "quantity": 300},
                    {"name": "Silver", "price": 250.00, "quantity": 800}
                ]
            }
        ]
        
        created_events = []
        
        for idx, event_data in enumerate(events_data):
            # Asignar organizador rotativo
            organizer = organizers[idx % len(organizers)]
            
            # Obtener categoría
            category = categories.get(event_data["category"])
            
            # Crear evento
            event = Event(
                title=event_data["title"],
                description=event_data["description"],
                startDate=event_data["startDate"],
                endDate=event_data["endDate"],
                venue=event_data["venue"],
                totalCapacity=event_data["totalCapacity"],
                status=event_data["status"],
                multimedia=event_data["multimedia"],
                organizer_id=organizer.id,
                category_id=category.id if category else None
            )
            
            db.add(event)
            db.flush()  # Para obtener el ID del evento
            
            # Crear tipos de tickets
            for tt_data in event_data["ticket_types"]:
                ticket_type = TicketType(
                    event_id=event.id,
                    name=tt_data["name"],
                    description=f"Ticket tipo {tt_data['name']} para {event.title}",
                    price=Decimal(str(tt_data["price"])),
                    quantity_available=tt_data["quantity"],
                    sold_quantity=random.randint(0, int(tt_data["quantity"] * 0.3)),  # Simular algunas ventas
                    is_active=True
                )
                db.add(ticket_type)
            
            created_events.append(event)
        
        db.commit()
        
        print("✅ Eventos de prueba creados exitosamente!")
        print(f"\n📊 Resumen:")
        print(f"   - Total eventos: {len(created_events)}")
        
        # Agrupar por categoría
        by_category = {}
        for event in created_events:
            cat_name = event.category.name if event.category else "Sin categoría"
            if cat_name not in by_category:
                by_category[cat_name] = 0
            by_category[cat_name] += 1
        
        print(f"\n   📂 Por categoría:")
        for cat, count in sorted(by_category.items()):
            print(f"      - {cat}: {count} eventos")
        
        # Agrupar por rango de fechas
        near_future = sum(1 for e in created_events if 0 < (e.startDate - today).days <= 30)
        mid_future = sum(1 for e in created_events if 30 < (e.startDate - today).days <= 60)
        far_future = sum(1 for e in created_events if (e.startDate - today).days > 60)
        past = sum(1 for e in created_events if (e.startDate - today).days < 0)
        
        print(f"\n   📅 Por fecha:")
        print(f"      - Pasados: {past}")
        print(f"      - Próximos 30 días: {near_future}")
        print(f"      - 30-60 días: {mid_future}")
        print(f"      - Más de 60 días: {far_future}")
        
        # Agrupar por rango de precio
        free = sum(1 for e in created_events for tt in e.ticket_types if float(tt.price) == 0)
        cheap = sum(1 for e in created_events for tt in e.ticket_types if 0 < float(tt.price) <= 100)
        medium = sum(1 for e in created_events for tt in e.ticket_types if 100 < float(tt.price) <= 300)
        expensive = sum(1 for e in created_events for tt in e.ticket_types if float(tt.price) > 300)
        
        print(f"\n   💰 Tipos de tickets por precio:")
        print(f"      - Gratuitos: {free}")
        print(f"      - S/ 0-100: {cheap}")
        print(f"      - S/ 100-300: {medium}")
        print(f"      - S/ 300+: {expensive}")
        
        print(f"\n✨ Los eventos están listos para probar filtros de búsqueda!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear eventos: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    """Ejecutar todos los seeders de testing"""
    print("🌱 Iniciando creación de datos de prueba...\n")
    
    print("=" * 60)
    print("PASO 1: Creando usuarios organizadores")
    print("=" * 60)
    create_test_users()
    
    print("\n" + "=" * 60)
    print("PASO 2: Creando eventos de prueba")
    print("=" * 60)
    create_test_events()
    
    print("\n✅ ¡Proceso completado!")
    print("\n📝 Para probar los filtros de búsqueda, puedes usar:")
    print("   - Categorías: conciertos, deportes, arte-cultura, festivales, etc.")
    print("   - Fechas: próximos días, próximas semanas, próximos meses")
    print("   - Precios: gratuitos, económicos, premium")
    print("   - Lugares: Lima, Miraflores, San Isidro, Barranco, etc.")
    print("   - Estado: PUBLISHED, COMPLETED")


if __name__ == "__main__":
    main()
