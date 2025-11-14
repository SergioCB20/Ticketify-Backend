"""
Script para resetear la base de datos
Ejecutar: python -m app.seeds.reset_database
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import inspect as sqlalchemy_inspect
from app.core.database import SessionLocal, engine
from app.core.database import Base


def reset_database():
    """Elimina y recrea todas las tablas"""
    print("=" * 70)
    print("🗑️  RESET DATABASE - Ticketify")
    print("=" * 70)
    print("\n⚠️  ADVERTENCIA: Esta operación:")
    print("   - Eliminará TODAS las tablas de la base de datos")
    print("   - Perderás TODOS los datos existentes")
    print("   - Recreará las tablas con la estructura actualizada")
    print("   - Sincronizará los modelos con la base de datos")
    
    response = input("\n¿Deseas continuar? (escribe 'SI' en mayúsculas): ")
    
    if response != "SI":
        print("\n❌ Operación cancelada")
        return
    
    try:
        print("\n🔍 Inspeccionando base de datos...")
        inspector = sqlalchemy_inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"   📊 Tablas encontradas: {len(existing_tables)}")
        
        if existing_tables:
            print("\n🗑️  Eliminando todas las tablas...")
            Base.metadata.drop_all(bind=engine)
            print("   ✅ Tablas eliminadas")
        else:
            print("   📌 Base de datos vacía")
        
        print("\n🔨 Recreando tablas con estructura actualizada...")
        Base.metadata.create_all(bind=engine)
        
        # Verificar tablas creadas
        inspector = sqlalchemy_inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"   ✅ {len(new_tables)} tablas creadas")
        
        # Mostrar algunas tablas principales
        main_tables = [t for t in new_tables if t in ['users', 'events', 'tickets', 'marketplace_listings', 'payments']]
        if main_tables:
            print("\n📋 Tablas principales:")
            for table in main_tables:
                print(f"   • {table}")
        
        print("\n" + "=" * 70)
        print("✅ BASE DE DATOS RESETEADA EXITOSAMENTE")
        print("=" * 70)
        print("\n👉 Próximos pasos:")
        print("   1. Ejecuta: python -m app.seeds.seed_data")
        print("   2. Inicia el servidor: python run.py")
        print("   3. Accede a: http://localhost:8000/docs")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al resetear la base de datos: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    reset_database()
