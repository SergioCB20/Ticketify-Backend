# -*- coding: utf-8 -*-
"""
Script para insertar eventos de prueba con todas sus relaciones
Ejecutar después de seed_initial_data.py
"""

from datetime import datetime, timedelta
from decimal import Decimal
from app.core.database import SessionLocal
from app.models import (
    User, Role, Event, EventCategory, TicketType, EventStatus
)
from passlib.context import CryptContext

# Configuración de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_organizer_users():
    """Crear usuarios organizadores de prueba"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen organizadores
        existing_organizer = db.query(User).filter(User.email == "organizer1@ticketify.com").first()
        if existing_organizer:
            print("⚠️  Los organizadores ya existen, saltando creación...")
            db.close()
            return
        
        # Obtener el rol de organizador
        organizer_role = db.query(Role).filter(Role.name == "Organizer").first()
        if not organizer_role:
            print("❌ Error: No existe el rol 'Organizer'. Ejecuta primero seed_initial_data.py")
            db.close()
            return
        
        organizers = [
            {
                "email": "organizer1@ticketify.com",
                "password": get_password_hash("Organizer123!"),
                "firstName": "Carlos",
                "lastName": "Méndez",
                "phoneNumber": "+51987654321",
                "documentId": "12345678",
                "isActive": True
            },
            {
                "email": "organizer2@ticketify.com",
                "password": get_password_hash("Organizer123!"),
                "firstName": "María",
                "lastName": "Rodríguez",
                "phoneNumber": "+51987654322",
                "documentId": "87654321",
                "isActive": True
            },
            {
                "email": "organizer3@ticketify.com",
                "password": get_password_hash("Organizer123!"),
                "firstName": "Jorge",
                "lastName": "Fernández",
                "phoneNumber": "+51987654323",
                "documentId": "11223344",
                "isActive": True
            },
            {
                "email": "organizer4@ticketify.com",
                "password": get_password_hash("Organizer123!"),
                "firstName": "Ana",
                "lastName": "Torres",
                "phoneNumber": "+51987654324",
                "documentId": "44332211",
                "isActive": True
            }
        ]
        
        created_organizers = []
        for org_data in organizers:
            organizer = User(**org_data)
            organizer.roles.append(organizer_role)
            db.add(organizer)
            created_organizers.append(organizer)
        
        db.commit()
        
        print(f"✅ {len(created_organizers)} organizadores creados exitosamente")
        for org in created_organizers:
            print(f"   - {org.email} ({org.firstName} {org.lastName})")
        
        db.close()
        return created_organizers
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear organizadores: {e}")
        db.close()
        return None


def create_events_with_tickets():
    """Crear eventos de prueba con sus tipos de tickets"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen eventos
        existing_event = db.query(Event).first()
        if existing_event:
            print("⚠️  Los eventos ya existen, saltando creación...")
            db.close()
            return
        
        # Obtener organizadores
        organizers = db.query(User).join(User.roles).filter(Role.name == "Organizer").all()
        if not organizers:
            print("❌ Error: No existen organizadores. Ejecuta la función create_organizer_users() primero")
            db.close()
            return
        
        # Obtener categorías
        categories = {
            "conciertos": db.query(EventCategory).filter(EventCategory.slug == "conciertos").first(),
            "deportes": db.query(EventCategory).filter(EventCategory.slug == "deportes").first(),
            "arte-cultura": db.query(EventCategory).filter(EventCategory.slug == "arte-cultura").first(),
            "festivales": db.query(EventCategory).filter(EventCategory.slug == "festivales").first(),
            "cursos-talleres": db.query(EventCategory).filter(EventCategory.slug == "cursos-talleres").first(),
            "entretenimiento": db.query(EventCategory).filter(EventCategory.slug == "entretenimiento").first(),
            "cine": db.query(EventCategory).filter(EventCategory.slug == "cine").first(),
            "comidas-bebidas": db.query(EventCategory).filter(EventCategory.slug == "comidas-bebidas").first(),
        }
        
        # Fechas para los eventos
        now = datetime.now()
        
        # EVENTOS VARIADOS PARA PRUEBAS DE FILTROS
        events_data = [
            # CONCIERTOS
            {
                "title": "Rock en Español - Tributo a los 90s",
                "description": "Revive los mejores éxitos del rock en español de los años 90 con bandas tributo en vivo. Un concierto inolvidable con los clásicos que marcaron una generación.",
                "startDate": now + timedelta(days=15),
                "endDate": now + timedelta(days=15, hours=5),
                "venue": "Estadio Nacional de Lima",
                "totalCapacity": 5000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1501281668745-f7f57925c3b4?w=800",
                    "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800"
                ],
                "organizer": organizers[0],
                "category": categories["conciertos"],
                "tickets": [
                    {"name": "General", "description": "Entrada general", "price": Decimal("80.00"), "quantity": 3000, "max_purchase": 6},
                    {"name": "VIP", "description": "Zona preferencial con barra libre", "price": Decimal("150.00"), "quantity": 1000, "max_purchase": 4},
                    {"name": "Platinum", "description": "Meet & Greet + Mercancía exclusiva", "price": Decimal("250.00"), "quantity": 500, "max_purchase": 2}
                ]
            },
            {
                "title": "Festival de Jazz Internacional",
                "description": "Tres días de los mejores exponentes del jazz a nivel mundial. Disfruta de presentaciones en vivo de artistas internacionales y locales.",
                "startDate": now + timedelta(days=45),
                "endDate": now + timedelta(days=47),
                "venue": "Gran Teatro Nacional",
                "totalCapacity": 2000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1415201364774-f6f0bb35f28f?w=800"
                ],
                "organizer": organizers[1],
                "category": categories["conciertos"],
                "tickets": [
                    {"name": "Pase 1 Día", "description": "Acceso por un día", "price": Decimal("120.00"), "quantity": 1200, "max_purchase": 4},
                    {"name": "Pase 3 Días", "description": "Acceso completo al festival", "price": Decimal("280.00"), "quantity": 800, "max_purchase": 2}
                ]
            },
            
            # DEPORTES
            {
                "title": "Clásico del Fútbol Peruano - Lima vs. Callao",
                "description": "El partido más esperado del año. Una rivalidad histórica que enciende la pasión de miles de hinchas. ¡No te lo pierdas!",
                "startDate": now + timedelta(days=8),
                "endDate": now + timedelta(days=8, hours=2),
                "venue": "Estadio Monumental",
                "totalCapacity": 8000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800"
                ],
                "organizer": organizers[2],
                "category": categories["deportes"],
                "tickets": [
                    {"name": "Tribuna Norte", "description": "Tribuna popular", "price": Decimal("50.00"), "quantity": 4000, "max_purchase": 8},
                    {"name": "Tribuna Oriente", "description": "Vista lateral", "price": Decimal("80.00"), "quantity": 3000, "max_purchase": 6},
                    {"name": "Palco VIP", "description": "Palco exclusivo con catering", "price": Decimal("200.00"), "quantity": 500, "max_purchase": 4}
                ]
            },
            {
                "title": "Maratón de Lima 2025",
                "description": "42K de pura adrenalina por las calles de Lima. Participa en la carrera más importante del año. Incluye chip de cronometraje, medalla y polo oficial.",
                "startDate": now + timedelta(days=60),
                "endDate": now + timedelta(days=60, hours=6),
                "venue": "Circuito Costa Verde - Miraflores",
                "totalCapacity": 3000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1452626038306-9aae5e071dd3?w=800"
                ],
                "organizer": organizers[0],
                "category": categories["deportes"],
                "tickets": [
                    {"name": "42K Marathon", "description": "Maratón completa", "price": Decimal("100.00"), "quantity": 1500, "max_purchase": 1},
                    {"name": "21K Media Maratón", "description": "Media maratón", "price": Decimal("70.00"), "quantity": 1000, "max_purchase": 1},
                    {"name": "10K Familiar", "description": "Carrera familiar", "price": Decimal("40.00"), "quantity": 500, "max_purchase": 4}
                ]
            },
            
            # ARTE Y CULTURA
            {
                "title": "Exposición: Maestros del Arte Contemporáneo",
                "description": "Una exhibición única que reúne obras de los artistas contemporáneos más reconocidos de América Latina. Incluye instalaciones interactivas y talleres.",
                "startDate": now + timedelta(days=5),
                "endDate": now + timedelta(days=35),
                "venue": "Museo de Arte de Lima (MALI)",
                "totalCapacity": 1500,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1536924940846-227afb31e2a5?w=800"
                ],
                "organizer": organizers[3],
                "category": categories["arte-cultura"],
                "tickets": [
                    {"name": "Entrada General", "description": "Acceso a todas las salas", "price": Decimal("25.00"), "quantity": 1000, "max_purchase": 6},
                    {"name": "Entrada con Visita Guiada", "description": "Tour guiado por expertos", "price": Decimal("45.00"), "quantity": 500, "max_purchase": 4}
                ]
            },
            {
                "title": "Teatro: La Casa de Bernarda Alba",
                "description": "Obra maestra de Federico García Lorca. Una producción teatral de clase mundial con reconocidos actores peruanos.",
                "startDate": now + timedelta(days=20),
                "endDate": now + timedelta(days=20, hours=3),
                "venue": "Teatro Segura",
                "totalCapacity": 600,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1503095396549-807759245b35?w=800"
                ],
                "organizer": organizers[1],
                "category": categories["arte-cultura"],
                "tickets": [
                    {"name": "Platea", "description": "Butacas platea", "price": Decimal("60.00"), "quantity": 300, "max_purchase": 6},
                    {"name": "Balcón", "description": "Butacas balcón", "price": Decimal("40.00"), "quantity": 300, "max_purchase": 6}
                ]
            },
            
            # FESTIVALES
            {
                "title": "Mistura 2025 - Festival Gastronómico",
                "description": "La feria gastronómica más importante de Latinoamérica. Degusta lo mejor de la cocina peruana e internacional con los chefs más reconocidos.",
                "startDate": now + timedelta(days=30),
                "endDate": now + timedelta(days=33),
                "venue": "Costa Verde - San Miguel",
                "totalCapacity": 10000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800"
                ],
                "organizer": organizers[2],
                "category": categories["festivales"],
                "tickets": [
                    {"name": "Entrada 1 Día", "description": "Acceso por 1 día", "price": Decimal("30.00"), "quantity": 6000, "max_purchase": 8},
                    {"name": "Pase Completo", "description": "Acceso los 4 días", "price": Decimal("90.00"), "quantity": 3000, "max_purchase": 4},
                    {"name": "VIP Gourmet", "description": "Degustación exclusiva + masterclass", "price": Decimal("200.00"), "quantity": 1000, "max_purchase": 2}
                ]
            },
            {
                "title": "Festival de Música Electrónica - Lima Electronic",
                "description": "2 días de música electrónica con los mejores DJs internacionales. Escenarios múltiples con diferentes géneros: house, techno, trance y más.",
                "startDate": now + timedelta(days=50),
                "endDate": now + timedelta(days=51),
                "venue": "Jockey Club del Perú",
                "totalCapacity": 15000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800"
                ],
                "organizer": organizers[0],
                "category": categories["festivales"],
                "tickets": [
                    {"name": "Early Bird - 2 Días", "description": "Preventa especial", "price": Decimal("180.00"), "original_price": Decimal("250.00"), "quantity": 3000, "max_purchase": 4, "sale_end_date": now + timedelta(days=30)},
                    {"name": "General - 2 Días", "description": "Entrada regular", "price": Decimal("250.00"), "quantity": 8000, "max_purchase": 6},
                    {"name": "VIP - 2 Días", "description": "Área VIP + bebidas", "price": Decimal("400.00"), "quantity": 3000, "max_purchase": 4},
                    {"name": "Backstage Pass", "description": "Acceso backstage + meet & greet", "price": Decimal("800.00"), "quantity": 500, "max_purchase": 2}
                ]
            },
            
            # CURSOS Y TALLERES
            {
                "title": "Workshop: Fotografía Digital Avanzada",
                "description": "Aprende técnicas avanzadas de fotografía digital con profesionales del medio. Incluye práctica en exteriores y certificado.",
                "startDate": now + timedelta(days=12),
                "endDate": now + timedelta(days=14),
                "venue": "Centro Cultural Ccori Wasi",
                "totalCapacity": 40,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=800"
                ],
                "organizer": organizers[3],
                "category": categories["cursos-talleres"],
                "tickets": [
                    {"name": "Inscripción Individual", "description": "Workshop completo + certificado", "price": Decimal("350.00"), "quantity": 40, "max_purchase": 1}
                ]
            },
            {
                "title": "Curso: Cocina Italiana - Nivel Intermedio",
                "description": "Domina la cocina italiana con un chef certificado. 4 sesiones prácticas con degustación incluida. Recetas y material incluido.",
                "startDate": now + timedelta(days=25),
                "endDate": now + timedelta(days=28),
                "venue": "Le Cordon Bleu Lima",
                "totalCapacity": 30,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=800"
                ],
                "organizer": organizers[1],
                "category": categories["cursos-talleres"],
                "tickets": [
                    {"name": "Curso Completo", "description": "4 sesiones + material", "price": Decimal("480.00"), "quantity": 30, "max_purchase": 1}
                ]
            },
            
            # ENTRETENIMIENTO
            {
                "title": "Stand Up Comedy Night",
                "description": "Una noche de risas con los mejores comediantes del país. Show en vivo con humor para toda la familia (mayores de 15 años).",
                "startDate": now + timedelta(days=18),
                "endDate": now + timedelta(days=18, hours=3),
                "venue": "Teatro Auditorio Miraflores",
                "totalCapacity": 800,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800"
                ],
                "organizer": organizers[2],
                "category": categories["entretenimiento"],
                "tickets": [
                    {"name": "Platea", "description": "Butacas platea", "price": Decimal("70.00"), "quantity": 500, "max_purchase": 6},
                    {"name": "VIP Front Row", "description": "Primera fila + meet & greet", "price": Decimal("120.00"), "quantity": 300, "max_purchase": 4}
                ]
            },
            {
                "title": "Circo del Sol - Espectáculo Acuático",
                "description": "El espectáculo más impresionante del año. Acrobacias aéreas, coreografías acuáticas y efectos especiales en una producción única.",
                "startDate": now + timedelta(days=70),
                "endDate": now + timedelta(days=75),
                "venue": "Arena Perú",
                "totalCapacity": 5000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1464207687429-7505649dae38?w=800"
                ],
                "organizer": organizers[0],
                "category": categories["entretenimiento"],
                "tickets": [
                    {"name": "Zona C", "description": "Zona general", "price": Decimal("100.00"), "quantity": 2500, "max_purchase": 6},
                    {"name": "Zona B", "description": "Vista privilegiada", "price": Decimal("180.00"), "quantity": 1500, "max_purchase": 6},
                    {"name": "Zona A Premium", "description": "Mejores asientos", "price": Decimal("300.00"), "quantity": 1000, "max_purchase": 4}
                ]
            },
            
            # CINE
            {
                "title": "Festival de Cine Iberoamericano",
                "description": "7 días del mejor cine iberoamericano con premieres, conversatorios con directores y homenajes a grandes del cine.",
                "startDate": now + timedelta(days=40),
                "endDate": now + timedelta(days=46),
                "venue": "Cinemark - Centro Histórico",
                "totalCapacity": 2000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800"
                ],
                "organizer": organizers[3],
                "category": categories["cine"],
                "tickets": [
                    {"name": "Pase Diario", "description": "Acceso a proyecciones de un día", "price": Decimal("20.00"), "quantity": 1200, "max_purchase": 4},
                    {"name": "Pase Semanal", "description": "Acceso ilimitado 7 días", "price": Decimal("100.00"), "quantity": 800, "max_purchase": 2}
                ]
            },
            
            # COMIDAS Y BEBIDAS
            {
                "title": "Festival del Pisco Sour",
                "description": "Celebra la bebida nacional del Perú. Degustación de diferentes variedades de pisco sour preparadas por los mejores bartenders.",
                "startDate": now + timedelta(days=35),
                "endDate": now + timedelta(days=35, hours=8),
                "venue": "Parque Kennedy - Miraflores",
                "totalCapacity": 1500,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=800"
                ],
                "organizer": organizers[1],
                "category": categories["comidas-bebidas"],
                "tickets": [
                    {"name": "Entrada + 3 Degustaciones", "description": "Acceso + 3 pisco sours", "price": Decimal("45.00"), "quantity": 1000, "max_purchase": 4},
                    {"name": "Pase Premium", "description": "Degustación ilimitada + masterclass", "price": Decimal("90.00"), "quantity": 500, "max_purchase": 2}
                ]
            },
            
            # EVENTO PRÓXIMO (para pruebas de filtros por fecha)
            {
                "title": "Concierto Benéfico - Unidos por la Música",
                "description": "Concierto benéfico con múltiples artistas peruanos. Toda la recaudación se destinará a instituciones educativas de zonas rurales.",
                "startDate": now + timedelta(days=3),
                "endDate": now + timedelta(days=3, hours=4),
                "venue": "Explanada Municipal de Miraflores",
                "totalCapacity": 3000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800"
                ],
                "organizer": organizers[2],
                "category": categories["conciertos"],
                "tickets": [
                    {"name": "Donación Básica", "description": "Apoyo básico", "price": Decimal("30.00"), "quantity": 2000, "max_purchase": 8},
                    {"name": "Donación Plus", "description": "Apoyo destacado + merchandising", "price": Decimal("60.00"), "quantity": 1000, "max_purchase": 6}
                ]
            },
            
            # EVENTO LEJANO (para pruebas de filtros por fecha)
            {
                "title": "Año Nuevo 2026 - Fiesta en la Playa",
                "description": "Despide el 2025 y recibe el 2026 en la mejor fiesta de playa. DJs internacionales, fuegos artificiales y cena buffet.",
                "startDate": datetime(2025, 12, 31, 20, 0),
                "endDate": datetime(2026, 1, 1, 6, 0),
                "venue": "Club Regatas Lima - Chorrillos",
                "totalCapacity": 2000,
                "status": EventStatus.PUBLISHED,
                "multimedia": [
                    "https://images.unsplash.com/photo-1467810563316-b5476525c0f9?w=800"
                ],
                "organizer": organizers[0],
                "category": categories["festivales"],
                "tickets": [
                    {"name": "Early Bird", "description": "Preventa especial", "price": Decimal("150.00"), "original_price": Decimal("200.00"), "quantity": 500, "max_purchase": 4, "sale_end_date": now + timedelta(days=30)},
                    {"name": "General", "description": "Entrada general + cena", "price": Decimal("200.00"), "quantity": 1000, "max_purchase": 6},
                    {"name": "VIP Premium", "description": "Área VIP + open bar + cena gourmet", "price": Decimal("400.00"), "quantity": 500, "max_purchase": 4}
                ]
            }
        ]
        
        created_events = []
        
        for event_data in events_data:
            # Extraer los datos de tickets
            tickets_data = event_data.pop("tickets")
            
            # Crear el evento
            event = Event(**event_data)
            db.add(event)
            db.flush()  # Para obtener el ID del evento
            
            # Crear los tipos de tickets
            for ticket_data in tickets_data:
                ticket_type = TicketType(
                    event_id=event.id,
                    name=ticket_data["name"],
                    description=ticket_data["description"],
                    price=ticket_data["price"],
                    original_price=ticket_data.get("original_price"),
                    quantity_available=ticket_data["quantity"],
                    sold_quantity=0,
                    min_purchase=ticket_data.get("min_purchase", 1),
                    max_purchase=ticket_data.get("max_purchase", 10),
                    sale_start_date=ticket_data.get("sale_start_date"),
                    sale_end_date=ticket_data.get("sale_end_date"),
                    is_active=True,
                    is_featured=False,
                    sort_order=0
                )
                db.add(ticket_type)
            
            created_events.append(event)
        
        db.commit()
        
        print(f"\n✅ {len(created_events)} eventos creados exitosamente con sus tipos de tickets")
        print("\n📋 RESUMEN POR CATEGORÍA:")
        
        # Agrupar por categoría
        from collections import defaultdict
        events_by_category = defaultdict(list)
        for event in created_events:
            category_name = event.category.name if event.category else "Sin categoría"
            events_by_category[category_name].append(event)
        
        for category, events in sorted(events_by_category.items()):
            print(f"\n🏷️  {category} ({len(events)} eventos):")
            for event in events:
                ticket_types_count = len(event.ticket_types)
                date_str = event.startDate.strftime("%d/%m/%Y")
                print(f"   • {event.title}")
                print(f"     📅 {date_str} | 📍 {event.venue} | 🎫 {ticket_types_count} tipos de tickets")
        
        db.close()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear eventos: {e}")
        import traceback
        traceback.print_exc()
        db.close()


def main():
    """Ejecutar todos los seeders de eventos"""
    print("🌱 Iniciando seeding de eventos y datos de prueba...\n")
    print("=" * 70)
    
    print("\n1️⃣  CREANDO USUARIOS ORGANIZADORES")
    print("-" * 70)
    create_organizer_users()
    
    print("\n2️⃣  CREANDO EVENTOS CON TICKETS")
    print("-" * 70)
    create_events_with_tickets()
    
    print("\n" + "=" * 70)
    print("✅ Seeding de eventos completado exitosamente!")
    print("\n📌 CREDENCIALES DE ORGANIZADORES:")
    print("   Email: organizer1@ticketify.com | Password: Organizer123!")
    print("   Email: organizer2@ticketify.com | Password: Organizer123!")
    print("   Email: organizer3@ticketify.com | Password: Organizer123!")
    print("   Email: organizer4@ticketify.com | Password: Organizer123!")
    print("=" * 70)


if __name__ == "__main__":
    main()
