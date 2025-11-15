"""
Script para insertar categorías de eventos en la base de datos
Ejecutar con: python seed_categories.py
"""

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.event_category import EventCategory
from app.core.database import Base
import uuid

# Categorías con sus iconos y colores
CATEGORIES_DATA = [
    {
        "name": "Conciertos",
        "description": "Eventos musicales y conciertos en vivo",
        "slug": "conciertos",
        "icon": "🎵",
        "color": "#FF6B6B",
        "sort_order": 1,
        "is_active": True,
        "is_featured": True
    },
    {
        "name": "Deportes",
        "description": "Eventos deportivos y competencias",
        "slug": "deportes",
        "icon": "⚽",
        "color": "#4ECDC4",
        "sort_order": 2,
        "is_active": True,
        "is_featured": True
    },
    {
        "name": "Teatro",
        "description": "Obras de teatro y espectáculos",
        "slug": "teatro",
        "icon": "🎭",
        "color": "#95E1D3",
        "sort_order": 3,
        "is_active": True,
        "is_featured": True
    },
    {
        "name": "Conferencias",
        "description": "Conferencias y eventos profesionales",
        "slug": "conferencias",
        "icon": "📊",
        "color": "#F38181",
        "sort_order": 4,
        "is_active": True,
        "is_featured": False
    },
    {
        "name": "Festivales",
        "description": "Festivales y eventos culturales",
        "slug": "festivales",
        "icon": "🎉",
        "color": "#AA96DA",
        "sort_order": 5,
        "is_active": True,
        "is_featured": True
    },
    {
        "name": "Arte",
        "description": "Exposiciones y eventos artísticos",
        "slug": "arte",
        "icon": "🎨",
        "color": "#FCBAD3",
        "sort_order": 6,
        "is_active": True,
        "is_featured": False
    },
    {
        "name": "Comedia",
        "description": "Shows de comedia y stand-up",
        "slug": "comedia",
        "icon": "😄",
        "color": "#FFE66D",
        "sort_order": 7,
        "is_active": True,
        "is_featured": False
    },
    {
        "name": "Familia",
        "description": "Eventos familiares y para niños",
        "slug": "familia",
        "icon": "👨‍👩‍👧‍👦",
        "color": "#A8E6CF",
        "sort_order": 8,
        "is_active": True,
        "is_featured": False
    }
]


def seed_categories():
    """Insertar categorías en la base de datos"""
    
    # Crear engine y sesión
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🌱 Iniciando seed de categorías...")
        
        # Verificar si ya existen categorías
        existing_count = db.query(EventCategory).count()
        
        if existing_count > 0:
            print(f"⚠️  Ya existen {existing_count} categorías en la base de datos.")
            response = input("¿Deseas eliminar las existentes e insertar nuevas? (s/n): ")
            
            if response.lower() == 's':
                print("🗑️  Eliminando categorías existentes...")
                db.query(EventCategory).delete()
                db.commit()
                print("✅ Categorías eliminadas")
            else:
                print("❌ Operación cancelada")
                return
        
        # Insertar nuevas categorías
        print(f"\n📝 Insertando {len(CATEGORIES_DATA)} categorías...")
        
        for cat_data in CATEGORIES_DATA:
            category = EventCategory(
                id=uuid.uuid4(),
                name=cat_data["name"],
                description=cat_data["description"],
                slug=cat_data["slug"],
                icon=cat_data["icon"],
                color=cat_data["color"],
                sort_order=cat_data["sort_order"],
                is_active=cat_data["is_active"],
                is_featured=cat_data["is_featured"]
            )
            db.add(category)
            print(f"  ✓ {cat_data['icon']} {cat_data['name']}")
        
        db.commit()
        
        print(f"\n✅ ¡Seed completado exitosamente!")
        print(f"📊 Total de categorías insertadas: {len(CATEGORIES_DATA)}")
        
        # Mostrar categorías insertadas
        print("\n📋 Categorías en la base de datos:")
        categories = db.query(EventCategory).order_by(EventCategory.sort_order).all()
        for cat in categories:
            featured = "⭐" if cat.is_featured else "  "
            print(f"  {featured} {cat.icon} {cat.name} ({cat.slug})")
        
    except Exception as e:
        print(f"\n❌ Error durante el seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_categories()
