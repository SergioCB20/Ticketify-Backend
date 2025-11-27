"""
Script de verificación rápida para asignación de tickets
Verifica que haya usuarios asistentes y eventos con tickets disponibles
"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.event import Event, EventStatus
from app.models.role import Role


def verificar_para_tickets():
    """Verifica que el sistema esté listo para asignar tickets"""
    db = SessionLocal()
    
    print("\n" + "=" * 70)
    print("🔍 VERIFICACIÓN PARA ASIGNACIÓN DE TICKETS")
    print("=" * 70)
    
    errores = []
    advertencias = []
    
    try:
        # 1. Verificar usuarios asistentes
        print("\n1️⃣  Verificando usuarios asistentes...")
        attendee_role = db.query(Role).filter(Role.name == UserRole.ATTENDEE).first()
        
        if not attendee_role:
            print("   ❌ No existe el rol ATTENDEE")
            errores.append("Falta el rol ATTENDEE")
        else:
            attendees = db.query(User).join(User.roles).filter(Role.name == UserRole.ATTENDEE).all()
            if not attendees:
                print("   ❌ No hay usuarios con rol ATTENDEE")
                errores.append("No hay usuarios asistentes")
            else:
                print(f"   ✅ {len(attendees)} usuarios asistentes encontrados:")
                for att in attendees[:5]:  # Mostrar primeros 5
                    tickets = len(att.tickets) if att.tickets else 0
                    print(f"      • {att.email} - {att.firstName} {att.lastName}")
                    print(f"        Tickets: {tickets}, Activo: {'Sí' if att.isActive else 'No'}")
                if len(attendees) > 5:
                    print(f"      ... y {len(attendees) - 5} más")
        
        # 2. Verificar eventos publicados
        print("\n2️⃣  Verificando eventos publicados...")
        events = db.query(Event).filter(Event.status == EventStatus.PUBLISHED).all()
        
        if not events:
            print("   ❌ No hay eventos publicados")
            errores.append("No hay eventos publicados")
        else:
            print(f"   ✅ {len(events)} eventos publicados encontrados")
            
            # Verificar eventos con tickets disponibles
            events_con_tickets = []
            for event in events:
                ticket_types_disponibles = [
                    tt for tt in event.ticket_types 
                    if tt.is_active and (tt.quantity_available - tt.sold_quantity) > 0
                ]
                if ticket_types_disponibles:
                    events_con_tickets.append((event, ticket_types_disponibles))
            
            if not events_con_tickets:
                print("   ⚠️  Ningún evento tiene tickets disponibles")
                advertencias.append("No hay tickets disponibles en los eventos")
            else:
                print(f"   ✅ {len(events_con_tickets)} eventos con tickets disponibles:")
                for event, tts in events_con_tickets[:3]:  # Mostrar primeros 3
                    print(f"\n      📅 {event.title}")
                    print(f"         Fecha: {event.startDate.strftime('%Y-%m-%d %H:%M')}")
                    print(f"         Lugar: {event.venue}")
                    print(f"         Tickets disponibles: {len(tts)} tipos")
                    for tt in tts:
                        disponibles = tt.quantity_available - tt.sold_quantity
                        print(f"           • {tt.name}: S/ {tt.price} ({disponibles} disponibles)")
                if len(events_con_tickets) > 3:
                    print(f"\n      ... y {len(events_con_tickets) - 3} eventos más")
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN")
        print("=" * 70)
        
        if errores:
            print("\n❌ ERRORES CRÍTICOS:")
            for i, error in enumerate(errores, 1):
                print(f"   {i}. {error}")
        
        if advertencias:
            print("\n⚠️  ADVERTENCIAS:")
            for i, adv in enumerate(advertencias, 1):
                print(f"   {i}. {adv}")
        
        if not errores and not advertencias:
            print("\n✅ ¡SISTEMA LISTO PARA ASIGNAR TICKETS!")
            print("   Puedes ejecutar: python asignar_ticket_usuario.py")
        elif not errores:
            print("\n⚠️  Sistema funcional pero con advertencias")
            print("   Revisa las advertencias antes de continuar")
        else:
            print("\n❌ El sistema NO está listo")
            print("   Corrige los errores antes de asignar tickets")
        
        # Mostrar soluciones
        if errores or advertencias:
            print("\n💡 SOLUCIONES:")
            
            if "No hay usuarios asistentes" in errores:
                print("\n   Para crear usuario asistente:")
                print("   • Registrar nuevo usuario desde la aplicación")
                print("   • O ejecutar:")
                print("     from app.models.role import Role")
                print("     attendee_role = db.query(Role).filter(Role.name=='ATTENDEE').first()")
                print("     user.roles.append(attendee_role)")
                print("     db.commit()")
            
            if "No hay eventos publicados" in errores:
                print("\n   Para crear evento:")
                print("   python crear_evento_organizador.py")
            
            if "No hay tickets disponibles en los eventos" in advertencias:
                print("\n   Para agregar tickets a un evento:")
                print("   • Editar el evento desde la interfaz de organizador")
                print("   • O crear nuevo evento con tickets incluidos")
        
        print("\n" + "=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    verificar_para_tickets()
