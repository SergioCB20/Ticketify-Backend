"""
Script para arreglar Alembic y agregar la columna photo
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sqlalchemy import text, inspect
from app.core.database import engine

def fix_alembic_and_database():
    """Arreglar estado de Alembic y agregar columna photo"""
    print("=" * 70)
    print("🔧 ARREGLANDO BASE DE DATOS Y ALEMBIC")
    print("=" * 70)
    
    with engine.connect() as conn:
        # 1. Verificar tabla alembic_version
        print("\n1️⃣ Verificando tabla alembic_version...")
        try:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.fetchone()
            if current_version:
                print(f"   📌 Versión actual: {current_version[0]}")
            else:
                print("   ⚠️  No hay versión registrada")
        except Exception as e:
            print(f"   ⚠️  Error al leer alembic_version: {e}")
        
        # 2. Limpiar y establecer versión correcta
        print("\n2️⃣ Limpiando y estableciendo versión correcta de Alembic...")
        try:
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('a41d8524fd5e')"))
            conn.commit()
            print("   ✅ Versión de Alembic actualizada a: a41d8524fd5e")
        except Exception as e:
            print(f"   ⚠️  Error al actualizar alembic_version: {e}")
            conn.rollback()
        
        # 3. Verificar y agregar columna photo
        print("\n3️⃣ Verificando columna photo en tabla events...")
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('events')]
        
        print(f"   📋 Columnas actuales: {', '.join(columns)}")
        
        if 'photo' not in columns:
            print("   ⚠️  La columna 'photo' no existe. Agregándola...")
            try:
                conn.execute(text("ALTER TABLE events ADD COLUMN photo BYTEA NULL"))
                conn.commit()
                print("   ✅ Columna 'photo' agregada exitosamente!")
            except Exception as e:
                print(f"   ❌ Error al agregar columna: {e}")
                conn.rollback()
        else:
            print("   ✅ La columna 'photo' ya existe")
        
        # 4. Verificar resultado final
        print("\n4️⃣ Verificación final...")
        inspector = inspect(engine)
        final_columns = [col['name'] for col in inspector.get_columns('events')]
        print(f"   📋 Columnas finales: {', '.join(final_columns)}")
        
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        final_version = result.fetchone()
        print(f"   📌 Versión final de Alembic: {final_version[0] if final_version else 'Ninguna'}")
    
    print("\n" + "=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print("\n💡 Ahora puedes ejecutar: python -m app.seeds.seed_data")
    print("=" * 70)

if __name__ == "__main__":
    try:
        fix_alembic_and_database()
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
