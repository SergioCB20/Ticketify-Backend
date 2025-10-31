# -*- coding: utf-8 -*-
"""
Script maestro para inicializar toda la base de datos con datos de prueba
Ejecuta los seeds en el orden correcto
"""

import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Ejecutar todos los seeds en orden"""
    
    print("=" * 70)
    print("🚀 INICIALIZANDO BASE DE DATOS CON DATOS DE PRUEBA")
    print("=" * 70)
    print()
    
    # PASO 1: Crear roles, permisos y categorías
    print("📋 PASO 1/2: Creando datos iniciales (roles, permisos, categorías)")
    print("-" * 70)
    try:
        from seed_initial_data import main as seed_initial
        seed_initial()
        print("\n✅ Datos iniciales creados correctamente\n")
    except Exception as e:
        print(f"\n❌ Error en datos iniciales: {e}")
        print("Continuando con el siguiente paso...\n")
    
    # PASO 2: Crear usuarios y eventos de prueba
    print("=" * 70)
    print("🎭 PASO 2/2: Creando usuarios y eventos de prueba")
    print("-" * 70)
    try:
        from seed_events_for_testing import main as seed_events
        seed_events()
        print("\n✅ Eventos de prueba creados correctamente\n")
    except Exception as e:
        print(f"\n❌ Error al crear eventos: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("=" * 70)
    print("🎉 ¡BASE DE DATOS INICIALIZADA COMPLETAMENTE!")
    print("=" * 70)
    print()
    print("📊 Datos disponibles:")
    print("   ✓ Roles y Permisos del sistema")
    print("   ✓ 10 Categorías de eventos")
    print("   ✓ 3 Usuarios organizadores")
    print("   ✓ 18+ Eventos de prueba con diferentes características")
    print("   ✓ Múltiples tipos de tickets por evento")
    print()
    print("🔐 Credenciales de prueba:")
    print("   Email: organizador1@test.com")
    print("   Email: organizador2@test.com")
    print("   Email: organizador3@test.com")
    print("   Password (para todos): Test123!")
    print()
    print("🧪 Los datos están listos para probar:")
    print("   - Filtros por categoría")
    print("   - Filtros por fecha")
    print("   - Filtros por precio")
    print("   - Búsqueda por texto")
    print("   - Paginación")
    print()


if __name__ == "__main__":
    main()
