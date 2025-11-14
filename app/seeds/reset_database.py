"""
Script para resetear la base de datos
Ejecutar: python -m app.seeds.reset_database
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.core.database import SessionLocal, engine
from app.core.database import Base


def reset_database():
    """Elimina y recrea todas las tablas"""
    print("=" * 70)
    print("🗑️  RESET DATABASE - Ticketify")
    print("=" * 70)
    
    response = input("\n⚠️  ADVERTENCIA: Esto eliminará TODOS los datos. ¿Continuar? (escribe 'SI'): ")
    
    if response != "SI":
        print("\n❌ Operación cancelada")
        return
    
    try:
        print("\n🗑️  Eliminando todas las tablas...")
        Base.metadata.drop_all(bind=engine)
        print("   ✅ Tablas eliminadas")
        
        print("\n🔨 Recreando tablas...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ Tablas creadas")
        
        print("\n" + "=" * 70)
        print("✅ BASE DE DATOS RESETEADA EXITOSAMENTE")
        print("=" * 70)
        print("\n💡 Ahora puedes ejecutar: python -m app.seeds.seed_data")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al resetear la base de datos: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    reset_database()
