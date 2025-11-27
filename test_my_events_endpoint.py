"""
Script de prueba para endpoint /api/events/my-events
Verifica que el endpoint devuelva los eventos del organizador correctamente
"""
import sys
import requests
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.role import Role


def test_my_events_endpoint():
    """Prueba el endpoint /my-events"""
    db = SessionLocal()
    
    print("\n" + "=" * 70)
    print("🧪 PRUEBA DE ENDPOINT /api/events/my-events")
    print("=" * 70)
    
    try:
        # 1. Obtener un organizador
        print("\n1️⃣  Buscando usuario organizador...")
        organizer_role = db.query(Role).filter(Role.name == UserRole.ORGANIZER).first()
        
        if not organizer_role:
            print("❌ No existe el rol ORGANIZER")
            return
        
        organizer = db.query(User).join(User.roles).filter(Role.name == UserRole.ORGANIZER).first()
        
        if not organizer:
            print("❌ No hay usuarios organizadores")
            return
        
        print(f"✅ Usuario encontrado: {organizer.email}")
        print(f"   ID: {organizer.id}")
        print(f"   Nombre: {organizer.firstName} {organizer.lastName}")
        
        # 2. Login para obtener token
        print("\n2️⃣  Obteniendo token de autenticación...")
        login_url = "http://localhost:8000/api/auth/login"
        
        # Necesitamos la contraseña - para pruebas, asumimos que es conocida
        password = input(f"\nIngresa la contraseña para {organizer.email}: ")
        
        login_response = requests.post(
            login_url,
            json={
                "email": organizer.email,
                "password": password
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("❌ No se recibió access_token")
            return
        
        print("✅ Token obtenido correctamente")
        
        # 3. Llamar al endpoint /my-events
        print("\n3️⃣  Llamando a /api/events/my-events...")
        my_events_url = "http://localhost:8000/api/events/my-events"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(my_events_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
        
        events = response.json()
        
        print(f"✅ Endpoint funcionando correctamente")
        print(f"\n📊 RESULTADO:")
        print(f"   Total de eventos: {len(events)}")
        
        if events:
            print(f"\n📋 EVENTOS ENCONTRADOS:")
            for i, event in enumerate(events, 1):
                print(f"\n   {i}. {event.get('title')}")
                print(f"      ID: {event.get('id')}")
                print(f"      Fecha: {event.get('date')}")
                print(f"      Lugar: {event.get('location')}")
                print(f"      Estado: {event.get('status')}")
                print(f"      Tickets: {event.get('soldTickets')}/{event.get('totalTickets')}")
                if event.get('imageUrl'):
                    print(f"      Imagen: {event.get('imageUrl')}")
        else:
            print("\n   ℹ️  El organizador no tiene eventos creados aún")
        
        print("\n" + "=" * 70)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("\n🧪 PRUEBA DE ENDPOINT - TICKETIFY")
    print("Este script prueba que el endpoint /api/events/my-events funcione")
    print("\nAsegúrate de que:")
    print("1. El backend esté corriendo (python run.py)")
    print("2. Tengas un usuario organizador con contraseña conocida")
    print("3. El organizador tenga al menos un evento creado")
    
    continuar = input("\n¿Continuar con la prueba? (s/N): ").strip().lower()
    
    if continuar == 's':
        test_my_events_endpoint()
    else:
        print("\n👋 Prueba cancelada")
