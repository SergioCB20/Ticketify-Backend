"""
Script para verificar la sincronización entre modelos y base de datos
Ejecutar: python -m app.seeds.verify_database
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import inspect, text
from app.core.database import engine
from app.models import Base


def get_model_columns(model):
    """Obtener columnas del modelo SQLAlchemy"""
    return {col.name: str(col.type) for col in model.__table__.columns}


def get_table_columns(table_name, inspector):
    """Obtener columnas de la tabla en la base de datos"""
    try:
        columns = inspector.get_columns(table_name)
        return {col['name']: str(col['type']) for col in columns}
    except Exception:
        return None


def verify_database():
    """Verificar sincronización entre modelos y base de datos"""
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE BASE DE DATOS - Ticketify")
    print("=" * 70)
    
    try:
        # Conectar a la base de datos
        inspector = inspect(engine)
        db_tables = set(inspector.get_table_names())
        
        print("\n📊 Información General:")
        print(f"   • Tablas en la base de datos: {len(db_tables)}")
        
        # Obtener modelos de SQLAlchemy
        model_tables = set(Base.metadata.tables.keys())
        print(f"   • Tablas en los modelos: {len(model_tables)}")
        
        # Comparar tablas
        print("\n🔄 Comparación de Tablas:")
        
        missing_in_db = model_tables - db_tables
        if missing_in_db:
            print(f"\n   ⚠️  Tablas en modelos pero NO en BD:")
            for table in sorted(missing_in_db):
                print(f"      • {table}")
        
        extra_in_db = db_tables - model_tables
        if extra_in_db:
            print(f"\n   ℹ️  Tablas en BD pero NO en modelos:")
            for table in sorted(extra_in_db):
                print(f"      • {table}")
        
        if not missing_in_db and not extra_in_db:
            print("   ✅ Todas las tablas están sincronizadas")
        
        # Verificar columnas de tablas importantes
        important_tables = ['users', 'events', 'tickets', 'marketplace_listings']
        
        print("\n📋 Verificación de Columnas (Tablas Importantes):")
        
        issues_found = False
        
        for table_name in important_tables:
            if table_name not in db_tables:
                print(f"\n   ❌ {table_name}: NO EXISTE EN LA BASE DE DATOS")
                issues_found = True
                continue
            
            if table_name not in model_tables:
                print(f"\n   ⚠️  {table_name}: No hay modelo definido")
                continue
            
            # Obtener modelo
            model = None
            for mapper in Base.registry.mappers:
                if mapper.class_.__tablename__ == table_name:
                    model = mapper.class_
                    break
            
            if not model:
                continue
            
            model_cols = get_model_columns(model)
            db_cols = get_table_columns(table_name, inspector)
            
            if db_cols is None:
                print(f"\n   ❌ {table_name}: Error al leer columnas de la BD")
                issues_found = True
                continue
            
            missing_cols = set(model_cols.keys()) - set(db_cols.keys())
            extra_cols = set(db_cols.keys()) - set(model_cols.keys())
            
            if missing_cols or extra_cols:
                print(f"\n   ⚠️  {table_name}:")
                if missing_cols:
                    print(f"      Columnas en modelo pero NO en BD:")
                    for col in sorted(missing_cols):
                        print(f"         • {col} ({model_cols[col]})")
                    issues_found = True
                
                if extra_cols:
                    print(f"      Columnas en BD pero NO en modelo:")
                    for col in sorted(extra_cols):
                        print(f"         • {col} ({db_cols[col]})")
            else:
                print(f"\n   ✅ {table_name}: Todas las columnas sincronizadas ({len(model_cols)} columnas)")
        
        # Verificar específicamente el campo problemático
        print("\n🔬 Verificación Específica - Campo profilePhotoMimeType:")
        
        if 'users' in db_tables:
            user_cols = get_table_columns('users', inspector)
            if user_cols and 'profilePhotoMimeType' in user_cols:
                print("   ✅ Campo 'profilePhotoMimeType' EXISTE en la tabla users")
                print(f"      Tipo: {user_cols['profilePhotoMimeType']}")
            else:
                print("   ❌ Campo 'profilePhotoMimeType' NO EXISTE en la tabla users")
                print("   💡 Ejecuta: python -m app.seeds.reset_database")
                issues_found = True
        
        # Resumen final
        print("\n" + "=" * 70)
        if issues_found:
            print("⚠️  SE ENCONTRARON PROBLEMAS DE SINCRONIZACIÓN")
            print("=" * 70)
            print("\n💡 Solución Recomendada:")
            print("   1. Ejecuta: python -m app.seeds.reset_database")
            print("   2. Ejecuta: python -m app.seeds.seed_data")
            print("   3. Vuelve a verificar con este script")
        else:
            print("✅ BASE DE DATOS CORRECTAMENTE SINCRONIZADA")
            print("=" * 70)
            print("\n✨ Todo está en orden. Puedes iniciar el servidor:")
            print("   python run.py")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error al verificar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    verify_database()
