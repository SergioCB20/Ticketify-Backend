# -*- coding: utf-8 -*-
"""
Script para forzar actualización de colores de categorías usando SQLAlchemy Core
Útil cuando el script normal no funciona por problemas de sesión
"""

from sqlalchemy import text
from app.core.database import engine

def update_colors_with_sql():
    """Actualizar colores usando SQL directo"""
    
    updates = [
        ("arte-cultura", "#8B5CF6", "Arte & Cultura - purple-500"),
        ("ayuda-social", "#10B981", "Ayuda Social - emerald-500"),
        ("cine", "#EC4899", "Cine - pink-500"),
        ("comidas-bebidas", "#F59E0B", "Comidas & Bebidas - amber-500"),
        ("conciertos", "#EF4444", "Conciertos - red-500"),
        ("cursos-talleres", "#06B6D4", "Cursos y talleres - cyan-500"),
        ("deportes", "#3B82F6", "Deportes - blue-500"),
        ("donacion", "#F43F5E", "Donación - rose-500"),
        ("entretenimiento", "#6366F1", "Entretenimiento - indigo-500"),
        ("festivales", "#EAB308", "Festivales - yellow-500"),
    ]
    
    try:
        with engine.connect() as conn:
            for slug, color, description in updates:
                result = conn.execute(
                    text("""
                        UPDATE event_categories 
                        SET color = :color, updated_at = NOW() 
                        WHERE slug = :slug
                    """),
                    {"color": color, "slug": slug}
                )
                conn.commit()
                print(f"✅ {description} -> {color}")
            
            # Verificar los cambios
            print("\n📋 Colores actualizados:")
            result = conn.execute(
                text("""
                    SELECT name, slug, icon, color 
                    FROM event_categories 
                    ORDER BY sort_order
                """)
            )
            
            for row in result:
                print(f"   {row.icon} {row.name:25} ({row.slug:20}) -> {row.color}")
            
            print("\n✅ Actualización completada exitosamente!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    print("🎨 Actualizando colores de categorías con SQL directo...\n")
    update_colors_with_sql()
