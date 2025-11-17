"""
Script todo-en-uno para configurar la base de datos desde cero
Ejecutar: python -m app.seeds.setup_all
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import subprocess
import time


def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(number, text):
    """Imprime un paso numerado"""
    print(f"\n📍 PASO {number}: {text}")
    print("-" * 70)


def run_script(script_path, description):
    """Ejecuta un script Python y maneja errores"""
    try:
        print(f"\n🔄 Ejecutando {description}...")
        result = subprocess.run(
            [sys.executable, "-m", script_path],
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}")
        print(f"   Código de salida: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado en {description}: {e}")
        return False


def setup_all():
    """Ejecuta todos los scripts de configuración en orden"""
    print_header("🚀 CONFIGURACIÓN COMPLETA DE BASE DE DATOS - Ticketify")
    
    print("\n⚠️  ADVERTENCIA:")
    print("   Este script ejecutará automáticamente:")
    print("   1. reset_database.py - Eliminará TODAS las tablas y datos")
    print("   2. seed_data.py - Creará datos de prueba")
    print("   3. verify_database.py - Verificará que todo esté correcto")
    print()
    print("   ⚠️  TODOS LOS DATOS ACTUALES SE PERDERÁN ⚠️")
    
    response = input("\n¿Deseas continuar? (escribe 'SI' en mayúsculas): ")
    
    if response != "SI":
        print("\n❌ Configuración cancelada")
        return
    
    start_time = time.time()
    
    # Paso 1: Reset Database
    print_step(1, "RESET DATABASE")
    print("Eliminando y recreando todas las tablas...")
    
    # Importar y ejecutar directamente para controlar la confirmación
    try:
        from app.seeds.reset_database import reset_database
        from app.core.database import SessionLocal, engine, Base
        from sqlalchemy import inspect
        
        print("\n🔍 Inspeccionando base de datos...")
        inspector = inspect(engine)
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
        
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"   ✅ {len(new_tables)} tablas creadas")
        
        main_tables = [t for t in new_tables if t in ['users', 'events', 'tickets', 'marketplace_listings', 'payments']]
        if main_tables:
            print("\n📋 Tablas principales:")
            for table in main_tables:
                print(f"   • {table}")
        
    except Exception as e:
        print(f"❌ Error en reset_database: {e}")
        return
    
    time.sleep(1)
    
    # Paso 2: Seed Data
    print_step(2, "SEED DATA")
    print("Poblando con datos de prueba...")
    
    try:
        from app.seeds.seed_data import seed_database
        seed_database()
    except Exception as e:
        print(f"❌ Error en seed_data: {e}")
        return
    
    time.sleep(1)
    
    # Paso 3: Verify Database
    print_step(3, "VERIFY DATABASE")
    print("Verificando sincronización...")
    
    try:
        from app.seeds.verify_database import verify_database
        verify_database()
    except Exception as e:
        print(f"❌ Error en verify_database: {e}")
        return
    
    # Resumen final
    elapsed_time = time.time() - start_time
    
    print_header("✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    
    print(f"\n⏱️  Tiempo total: {elapsed_time:.2f} segundos")
    
    print("\n📝 Datos creados:")
    print("   • 5 categorías de eventos")
    print("   • 3 usuarios de prueba")
    print("   • 6 eventos de ejemplo")
    print("   • Tipos de tickets para cada evento")
    
    print("\n👥 Credenciales de prueba:")
    print("   Admin:       admin@ticketify.com / admin123")
    print("   Organizador: organizador@ticketify.com / org123")
    print("   Usuario:     usuario@ticketify.com / user123")
    
    print("\n🎯 Siguientes pasos:")
    print("   1. Inicia el servidor:")
    print("      python run.py")
    print()
    print("   2. Accede a la documentación:")
    print("      http://localhost:8000/docs")
    print()
    print("   3. Prueba el login con cualquiera de las credenciales")
    
    print("\n" + "=" * 70)
    print("🎉 ¡Todo listo para desarrollar!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        setup_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
