"""
Script de prueba para el sistema de mensajes a asistentes
Ejecutar después de aplicar la migración
"""
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models import EventMessage, Event, User, Ticket, TicketStatus
from app.repositories.event_message_repository import EventMessageRepository
from app.services.event_message_service import EventMessageService
from app.schemas.event_message import EventMessageCreate

def test_database_connection():
    """Probar conexión a la base de datos"""
    print("🔌 Probando conexión a la base de datos...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión exitosa a la base de datos")
            return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_table_exists():
    """Verificar que la tabla event_messages existe"""
    print("\n📋 Verificando tabla event_messages...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'event_messages'
                );
            """))
            exists = result.scalar()
            if exists:
                print("✅ Tabla event_messages existe")
                
                # Contar registros
                count_result = conn.execute(text("SELECT COUNT(*) FROM event_messages"))
                count = count_result.scalar()
                print(f"📊 Mensajes en la tabla: {count}")
                return True
            else:
                print("❌ Tabla event_messages NO existe. Ejecuta la migración:")
                print("   alembic upgrade head")
                return False
    except Exception as e:
        print(f"❌ Error al verificar tabla: {e}")
        return False

def test_get_attendees():
    """Probar obtención de asistentes de un evento"""
    print("\n👥 Probando obtención de asistentes...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Buscar un evento con tickets
        event = db.query(Event).join(Ticket).filter(
            Ticket.status == TicketStatus.ACTIVE
        ).first()
        
        if not event:
            print("⚠️  No hay eventos con tickets activos para probar")
            return False
        
        print(f"📅 Evento de prueba: {event.title}")
        
        service = EventMessageService(db)
        attendees = service.get_event_attendees(event.id)
        
        print(f"✅ Se encontraron {len(attendees)} asistentes")
        
        if attendees:
            print(f"\n📝 Ejemplo de asistente:")
            print(f"   Nombre: {attendees[0]['firstName']} {attendees[0]['lastName']}")
            print(f"   Email: {attendees[0]['email']}")
            print(f"   Tickets: {attendees[0]['ticketCount']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al obtener asistentes: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_creation():
    """Probar creación de un mensaje de prueba"""
    print("\n💬 Probando creación de mensaje...")
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Buscar un organizador con eventos
        organizer = db.query(User).join(Event).first()
        
        if not organizer:
            print("⚠️  No hay organizadores para probar")
            db.close()
            return False
        
        # Buscar un evento del organizador
        event = db.query(Event).filter(Event.organizer_id == organizer.id).first()
        
        if not event:
            print("⚠️  El organizador no tiene eventos")
            db.close()
            return False
        
        print(f"👤 Organizador: {organizer.full_name}")
        print(f"📅 Evento: {event.title}")
        
        # Crear mensaje de prueba
        repo = EventMessageRepository(db)
        message_data = EventMessageCreate(
            subject="Mensaje de prueba - Sistema funcionando",
            content="Este es un mensaje de prueba del sistema. Si lo ves, todo funciona correctamente.",
            message_type="BROADCAST"
        )
        
        message = repo.create_message(
            event_id=event.id,
            organizer_id=organizer.id,
            message_data=message_data
        )
        
        print(f"✅ Mensaje creado con ID: {message.id}")
        print(f"   Asunto: {message.subject}")
        print(f"   Tipo: {message.message_type}")
        
        # Actualizar estadísticas de prueba
        repo.update_message_stats(message.id, successful_sends=0, failed_sends=0)
        
        print(f"✅ Estadísticas actualizadas")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al crear mensaje: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("="*60)
    print("🧪 PRUEBAS DEL SISTEMA DE MENSAJES A ASISTENTES")
    print("="*60)
    
    tests = [
        ("Conexión a BD", test_database_connection),
        ("Tabla event_messages", test_table_exists),
        ("Obtener asistentes", test_get_attendees),
        ("Crear mensaje", test_message_creation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo para usar.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("\nSoluciones comunes:")
        print("1. Si falta la tabla: ejecuta 'alembic upgrade head'")
        print("2. Si no hay datos: crea eventos y vende algunos tickets de prueba")
        print("3. Verifica las credenciales de BD en el archivo .env")

if __name__ == "__main__":
    main()
