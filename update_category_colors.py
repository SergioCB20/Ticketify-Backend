# -*- coding: utf-8 -*-
"""
Script para actualizar los colores de las categorías con colores HEX válidos de Tailwind
"""

from app.core.database import SessionLocal
from app.models.event_category import EventCategory

def update_category_colors():
    """Actualizar colores de categorías con colores Tailwind"""
    db = SessionLocal()
    
    try:
        # Mapeo de categorías a colores HEX de Tailwind
        category_colors = {
            "arte-cultura": "#8B5CF6",  # purple-500
            "ayuda-social": "#10B981",  # emerald-500
            "cine": "#EC4899",          # pink-500
            "comidas-bebidas": "#F59E0B",  # amber-500
            "conciertos": "#EF4444",    # red-500
            "cursos-talleres": "#06B6D4",  # cyan-500
            "deportes": "#3B82F6",      # blue-500
            "donacion": "#F43F5E",      # rose-500
            "entretenimiento": "#6366F1",  # indigo-500
            "festivales": "#EAB308",    # yellow-500
        }
        
        # Actualizar cada categoría
        updated_count = 0
        for slug, color in category_colors.items():
            category = db.query(EventCategory).filter(EventCategory.slug == slug).first()
            if category:
                category.color = color
                updated_count += 1
                print(f"✅ Actualizado: {category.name} -> {color}")
            else:
                print(f"⚠️  Categoría no encontrada: {slug}")
        
        db.commit()
        print(f"\n✅ {updated_count} categorías actualizadas exitosamente")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al actualizar colores: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🎨 Actualizando colores de categorías...\n")
    update_category_colors()
