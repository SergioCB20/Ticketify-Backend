# -*- coding: utf-8 -*-
"""
Script de ejemplo para crear datos iniciales despues de la migracion
Ejecutar despues de aplicar: alembic upgrade head
"""

from app.core.database import SessionLocal
from app.models import (
    Role, Permission, UserRole, AdminRole,
    EventCategory
)
import uuid

def create_roles_and_permissions():
    """Crear roles y permisos basicos del sistema"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen permisos
        existing_permissions = db.query(Permission).first()
        if existing_permissions:
            print("⚠️  Los permisos ya existen, saltando creacion...")
            return
        
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
    """Crear categorias de eventos que coinciden con el frontend"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen categorias
        existing_categories = db.query(EventCategory).first()
        if existing_categories:
            print("⚠️  Las categorias ya existen, saltando creacion...")
            return
        
        categories = [
            EventCategory(
                name="Arte & Cultura",
                description="Exposiciones de arte, museos, galerias y eventos culturales",
                slug="arte-cultura",
                icon="🎨",
                color="#8B5CF6",  # purple-500
                sort_order=1,
                is_active=True,
                is_featured=True
            ),
            EventCategory(
                name="Ayuda Social",
                description="Eventos beneficos, recaudaciones de fondos y actividades solidarias",
                slug="ayuda-social",
                icon="🤝",
                color="#10B981",  # emerald-500
                sort_order=2,
                is_active=True,
                is_featured=False
            ),
            EventCategory(
                name="Cine",
                description="Peliculas, festivales de cine y proyecciones especiales",
                slug="cine",
                icon="🎬",
                color="#EC4899",  # pink-500
                sort_order=3,
                is_active=True,
                is_featured=True
            ),
            EventCategory(
                name="Comidas & Bebidas",
                description="Festivales gastronomicos, catas, degustaciones y eventos culinarios",
                slug="comidas-bebidas",
                icon="🍽️",
                color="#F59E0B",  # amber-500
                sort_order=4,
                is_active=True,
                is_featured=False
            ),
            EventCategory(
                name="Conciertos",
                description="Conciertos de musica en vivo, festivales musicales y shows",
                slug="conciertos",
                icon="🎵",
                color="#EF4444",  # red-500
                sort_order=5,
                is_active=True,
                is_featured=True
            ),
            EventCategory(
                name="Cursos y talleres",
                description="Talleres educativos, cursos, seminarios y capacitaciones",
                slug="cursos-talleres",
                icon="📚",
                color="#06B6D4",  # cyan-500
                sort_order=6,
                is_active=True,
                is_featured=False
            ),
            EventCategory(
                name="Deportes",
                description="Eventos deportivos, competencias, partidos y actividades fisicas",
                slug="deportes",
                icon="⚽",
                color="#3B82F6",  # blue-500
                sort_order=7,
                is_active=True,
                is_featured=True
            ),
            EventCategory(
                name="Donacion",
                description="Eventos de donacion, campanas solidarias y recaudaciones",
                slug="donacion",
                icon="❤️",
                color="#F43F5E",  # rose-500
                sort_order=8,
                is_active=True,
                is_featured=False
            ),
            EventCategory(
                name="Entretenimiento",
                description="Shows, espectaculos, performances y eventos de entretenimiento",
                slug="entretenimiento",
                icon="🎪",
                color="#6366F1",  # indigo-500
                sort_order=9,
                is_active=True,
                is_featured=True
            ),
            EventCategory(
                name="Festivales",
                description="Festivales de diversos tipos, ferias y celebraciones",
                slug="festivales",
                icon="🎉",
                color="#EAB308",  # yellow-500
                sort_order=10,
                is_active=True,
                is_featured=True
            ),
        ]
        
        db.add_all(categories)
        db.commit()
        
        print("✅ Categorias de eventos creadas exitosamente")
        print(f"   Total de categorias: {len(categories)}")
        for cat in categories:
            print(f"   - {cat.icon} {cat.name} ({cat.slug})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear categorias: {e}")
    finally:
        db.close()


def main():
    """Ejecutar todos los seeders"""
    print("🌱 Iniciando seeding de la base de datos...\n")
    
    create_roles_and_permissions()
    print()
    create_event_categories()
    
    print("\n✅ Seeding completado!")


if __name__ == "__main__":
    main()
