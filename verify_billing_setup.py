"""
Script de verificación del Sistema de Facturación
Verifica que todos los archivos y dependencias estén correctamente instalados
"""
import sys
from pathlib import Path

def check_files():
    """Verificar que todos los archivos necesarios existan"""
    print("🔍 Verificando archivos del módulo de facturación...\n")
    
    base_path = Path(__file__).resolve().parent / "app"
    
    required_files = {
        "API": base_path / "api" / "billing.py",
        "Service": base_path / "services" / "billing_service.py",
        "Repository": base_path / "repositories" / "billing_repository.py",
        "Schemas": base_path / "schemas" / "billing.py",
    }
    
    all_exist = True
    for name, file_path in required_files.items():
        if file_path.exists():
            print(f"✅ {name:15} → {file_path.name}")
        else:
            print(f"❌ {name:15} → NO ENCONTRADO: {file_path}")
            all_exist = False
    
    return all_exist


def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    print("\n🔍 Verificando dependencias...\n")
    
    dependencies = {
        "FastAPI": "fastapi",
        "SQLAlchemy": "sqlalchemy",
        "Pydantic": "pydantic",
        "MercadoPago": "mercadopago",
        "ReportLab": "reportlab",
        "OpenPyXL": "openpyxl",
    }
    
    all_installed = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name:15} → Instalado")
        except ImportError:
            print(f"❌ {name:15} → NO INSTALADO")
            all_installed = False
    
    return all_installed


def check_router_registration():
    """Verificar que el router esté registrado"""
    print("\n🔍 Verificando registro del router...\n")
    
    init_file = Path(__file__).resolve().parent / "app" / "api" / "__init__.py"
    
    if not init_file.exists():
        print("❌ Archivo __init__.py no encontrado")
        return False
    
    content = init_file.read_text()
    
    checks = {
        "Import del router": "from .billing import router as billing_router" in content,
        "Include del router": "api_router.include_router(billing_router)" in content,
    }
    
    all_registered = True
    for check_name, is_ok in checks.items():
        if is_ok:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name} → NO ENCONTRADO")
            all_registered = False
    
    return all_registered


def check_database_models():
    """Verificar que los modelos de DB necesarios existan"""
    print("\n🔍 Verificando modelos de base de datos...\n")
    
    base_path = Path(__file__).resolve().parent / "app" / "models"
    
    required_models = {
        "Event": base_path / "event.py",
        "Purchase": base_path / "purchase.py",
        "Payment": base_path / "payment.py",
        "User": base_path / "user.py",
    }
    
    all_exist = True
    for name, file_path in required_models.items():
        if file_path.exists():
            print(f"✅ {name:15} → {file_path.name}")
        else:
            print(f"❌ {name:15} → NO ENCONTRADO: {file_path}")
            all_exist = False
    
    return all_exist


def print_summary(files_ok, deps_ok, router_ok, models_ok):
    """Imprimir resumen final"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60 + "\n")
    
    status = {
        "Archivos del módulo": files_ok,
        "Dependencias Python": deps_ok,
        "Registro de router": router_ok,
        "Modelos de DB": models_ok,
    }
    
    for check, is_ok in status.items():
        status_icon = "✅" if is_ok else "❌"
        print(f"{status_icon} {check}")
    
    print("\n" + "="*60)
    
    if all(status.values()):
        print("🎉 ¡TODO CORRECTO! El sistema de facturación está listo.")
        print("="*60)
        print("\n📝 Próximos pasos:")
        print("1. Iniciar el servidor: python run.py")
        print("2. Acceder a la documentación: http://localhost:8000/docs")
        print("3. Probar endpoint: /api/organizer/billing/events")
        print("\n💡 Tip: Revisa BILLING_README.md para más información")
        return 0
    else:
        print("⚠️  ATENCIÓN: Se encontraron problemas.")
        print("="*60)
        print("\n🔧 Soluciones:")
        
        if not deps_ok:
            print("\n→ Instalar dependencias:")
            print("  pip install -r billing_requirements.txt")
        
        if not files_ok:
            print("\n→ Archivos faltantes:")
            print("  Asegúrate de haber copiado todos los archivos del módulo")
        
        if not router_ok:
            print("\n→ Router no registrado:")
            print("  Editar app/api/__init__.py y agregar:")
            print("  from .billing import router as billing_router")
            print("  api_router.include_router(billing_router)")
        
        if not models_ok:
            print("\n→ Modelos faltantes:")
            print("  Verifica la estructura de la base de datos")
        
        print("\n📖 Consulta BILLING_BACKEND_DOCUMENTATION.md para más ayuda")
        return 1


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DEL SISTEMA DE FACTURACIÓN")
    print("="*60 + "\n")
    
    files_ok = check_files()
    deps_ok = check_dependencies()
    router_ok = check_router_registration()
    models_ok = check_database_models()
    
    exit_code = print_summary(files_ok, deps_ok, router_ok, models_ok)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
