"""
Script de verificación para el sistema de creación de eventos
Verifica que todos los requisitos estén cumplidos antes de crear eventos
"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.event import Event
from app.models.event_category import EventCategory
from app.models.role import Role


def verificar_sistema():
    """Verifica que el sistema esté listo para crear eventos"""
    db = SessionLocal()
    
    print("\n" + "=" * 70)
    print("🔍 VERIFICACIÓN DEL SISTEMA - TICKETIFY")
    print("=" * 70)
    
    errores = []
    advertencias = []
    
    try:
        # 1. Verificar conexión a base de datos
        print("\n1️⃣  Verificando conexión a base de datos...")
        try:
            db.execute("SELECT 1")
            print("   ✅ Conexión exitosa")
        except Exception as e:
            print(f"   ❌ Error de conexión: {e}")
            errores.append("No se puede conectar a la base de datos")
        
        # 2. Verificar roles
        print("\n2️⃣  Verificando roles en la base de datos...")
        roles = db.query(Role).all()
        if not roles:
            print("   ❌ No hay roles en la base de datos")
            errores.append("Base de datos sin roles")
        else:
            print(f"   ✅ {len(roles)} roles encontrados")
            for role in roles:
                print(f"      • {role.name}")
        
        organizer_role = db.query(Role).filter(Role.name == UserRole.ORGANIZER).first()
        if not organizer_role:
            print("   ⚠️  No existe el rol ORGANIZER")
            advertencias.append("Falta el rol ORGANIZER - ejecuta las migraciones")
        else:
            print("   ✅ Rol ORGANIZER encontrado")
        
        # 3. Verificar usuarios
        print("\n3️⃣  Verificando usuarios...")
        users = db.query(User).all()
        if not users:
            print("   ❌ No hay usuarios en la base de datos")
            errores.append("No hay usuarios registrados")
        else:
            print(f"   ✅ {len(users)} usuarios encontrados")
            
            # Verificar usuarios activos
            active_users = db.query(User).filter(User.isActive == True).all()
            print(f"      • {len(active_users)} usuarios activos")
        
        # 4. Verificar organizadores
        print("\n4️⃣  Verificando usuarios organizadores...")
        if organizer_role:
            organizers = db.query(User).join(User.roles).filter(Role.name == UserRole.ORGANIZER).all()
            if not organizers:
                print("   ⚠️  No hay usuarios con rol ORGANIZER")
                advertencias.append("No hay organizadores - crea uno o asigna el rol a un usuario")
            else:
                print(f"   ✅ {len(organizers)} organizadores encontrados:")
                for org in organizers:
                    eventos = len(org.organized_events) if org.organized_events else 0
                    print(f"      • {org.email} - {org.firstName} {org.lastName}")
                    print(f"        ID: {org.id}")
                    print(f"        Activo: {'Sí' if org.isActive else 'No'}")
                    print(f"        Eventos creados: {eventos}")
                    print()
        
        # 5. Verificar categorías
        print("5️⃣  Verificando categorías de eventos...")
        categories = db.query(EventCategory).all()
        if not categories:
            print("   ⚠️  No hay categorías de eventos")
            advertencias.append("No hay categorías - los eventos se crearán sin categoría")
        else:
            print(f"   ✅ {len(categories)} categorías encontradas")
            active_cats = db.query(EventCategory).filter(EventCategory.is_active == True).all()
            print(f"      • {len(active_cats)} categorías activas:")
            for cat in active_cats[:5]:  # Mostrar solo las primeras 5
                print(f"        - {cat.name} ({cat.slug})")
            if len(active_cats) > 5:
                print(f"        ... y {len(active_cats) - 5} más")
        
        # 6. Verificar eventos existentes
        print("\n6️⃣  Verificando eventos existentes...")
        events = db.query(Event).all()
        print(f"   ℹ️  {len(events)} eventos en la base de datos")
        if events:
            from app.models.event import EventStatus
            published = db.query(Event).filter(Event.status == EventStatus.PUBLISHED).count()
            draft = db.query(Event).filter(Event.status == EventStatus.DRAFT).count()
            cancelled = db.query(Event).filter(Event.status == EventStatus.CANCELLED).count()
            print(f"      • Publicados: {published}")
            print(f"      • Borradores: {draft}")
            print(f"      • Cancelados: {cancelled}")
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE VERIFICACIÓN")
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
            print("\n✅ ¡TODO ESTÁ LISTO!")
            print("   Puedes ejecutar los scripts de creación de eventos sin problemas.")
        elif not errores:
            print("\n✅ Sistema funcional con advertencias")
            print("   Puedes crear eventos, pero revisa las advertencias.")
        else:
            print("\n❌ El sistema NO está listo")
            print("   Corrige los errores antes de crear eventos.")
        
        print("\n" + "=" * 70)
        
        # Mostrar comandos útiles
        print("\n💡 COMANDOS ÚTILES:")
        print("   • Crear evento interactivo:")
        print("     python crear_evento_organizador.py")
        print()
        print("   • Crear evento rápido por email:")
        print("     python crear_evento_simple.py email@organizador.com")
        print()
        if organizers:
            print("   • Crear evento para un organizador específico:")
            print(f"     python crear_evento_simple.py {organizers[0].email}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA VERIFICACIÓN: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    verificar_sistema()
