"""
Script de ejemplo para crear datos iniciales después de la migración
Ejecutar después de aplicar: alembic upgrade head
"""

from app.core.database import SessionLocal
from app.models import (
    Role, Permission, UserRole, AdminRole,
    EventCategory
)
import uuid

def create_roles_and_permissions():
    """Crear roles y permisos básicos del sistema"""
    db = SessionLocal()
    
    try:
        # Crear Permisos
        permissions = [
            Permission(code="event.create", name="Crear eventos", description="Permite crear nuevos eventos"),
            Permission(code="event.update", name="Actualizar eventos", description="Permite modificar eventos"),
            Permission(code="event.delete", name="Eliminar eventos", description="Permite eliminar eventos"),
            Permission(code="ticket.validate", name="Validar tickets", description="Permite validar tickets en entrada"),
            Permission(code="user.manage", name="Gestionar usuarios", description="Permite administrar usuarios"),
            Permission(code="dispute.resolve", name="Resolver disputas", description="Permite resolver disputas"),
            Permission(code="report.view", name="Ver reportes", description="Permite ver reportes y analytics"),
            Permission(code="payment.refund", name="Reembolsar pagos", description="Permite procesar reembolsos"),
        ]
        
        db.add_all(permissions)
        db.flush()
        
        # Crear Roles
        attendee_role = Role(
            name="Attendee",
            description="Usuario asistente a eventos"
        )
        
        organizer_role = Role(
            name="Organizer",
            description="Organizador de eventos"
        )
        # Asignar permisos a organizador
        organizer_role.permissions.extend([
            p for p in permissions if p.code.startswith("event.")
        ])
        
        super_admin_role = Role(
            name="Super Admin",
            description="Administrador con todos los permisos"
        )
        super_admin_role.permissions.extend(permissions)
        
        support_admin_role = Role(
            name="Support Admin",
            description="Administrador de soporte"
        )
        support_admin_role.permissions.extend([
            p for p in permissions if p.code in ["dispute.resolve", "user.manage", "ticket.validate"]
        ])
        
        db.add_all([attendee_role, organizer_role, super_admin_role, support_admin_role])
        db.commit()
        
        print("✅ Roles y permisos creados exitosamente")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear roles y permisos: {e}")
    finally:
        db.close()


def create_event_categories():
    """Crear categorías de eventos básicas"""
    db = SessionLocal()
    
    try:
        categories = [
            EventCategory(
                name="Música",
                description="Conciertos, festivales y eventos musicales",
                slug="musica",
                icon="🎵",
                color="#FF6B6B"
            ),
            EventCategory(
                name="Deportes",
                description="Eventos deportivos y competencias",
                slug="deportes",
                icon="⚽",
                color="#4ECDC4"
            ),
            EventCategory(
                name="Teatro",
                description="Obras de teatro y espectáculos",
                slug="teatro",
                icon="🎭",
                color="#95E1D3"
            ),
            EventCategory(
                name="Conferencias",
                description="Conferencias, seminarios y charlas",
                slug="conferencias",
                icon="💼",
                color="#F38181"
            ),
            EventCategory(
                name="Comedia",
                description="Stand-up comedy y espectáculos de humor",
                slug="comedia",
                icon="😂",
                color="#FECA57"
            ),
            EventCategory(
                name="Arte y Cultura",
                description="Exposiciones, museos y eventos culturales",
                slug="arte-cultura",
                icon="🎨",
                color="#A29BFE"
            ),
        ]
        
        db.add_all(categories)
        db.commit()
        
        print("✅ Categorías de eventos creadas exitosamente")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear categorías: {e}")
    finally:
        db.close()


def main():
    """Ejecutar todos los seeders"""
    print("🌱 Iniciando seeding de la base de datos...\n")
    
    create_roles_and_permissions()
    create_event_categories()
    
    print("\n✅ Seeding completado!")


if __name__ == "__main__":
    main()
