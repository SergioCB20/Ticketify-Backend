"""
Script de verificación completa del Sistema de Facturación
Verifica que todos los componentes estén correctamente instalados y configurados
"""
import sys
import os

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Imprimir encabezado"""
    print(f"\n{BOLD}{BLUE}{'='*60}{ENDC}")
    print(f"{BOLD}{BLUE}{text.center(60)}{ENDC}")
    print(f"{BOLD}{BLUE}{'='*60}{ENDC}\n")


def print_success(text):
    """Imprimir mensaje de éxito"""
    print(f"{GREEN}✅ {text}{ENDC}")


def print_error(text):
    """Imprimir mensaje de error"""
    print(f"{RED}❌ {text}{ENDC}")


def print_warning(text):
    """Imprimir mensaje de advertencia"""
    print(f"{YELLOW}⚠️  {text}{ENDC}")


def print_info(text):
    """Imprimir mensaje informativo"""
    print(f"{BLUE}ℹ️  {text}{ENDC}")


def check_python_version():
    """Verificar versión de Python"""
    print_header("Verificación de Python")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (se requiere 3.8+)")
        return False


def check_dependencies():
    """Verificar dependencias instaladas"""
    print_header("Verificación de Dependencias")
    
    dependencies = {
        'fastapi': 'FastAPI',
        'sqlalchemy': 'SQLAlchemy',
        'pydantic': 'Pydantic',
        'mercadopago': 'MercadoPago SDK',
        'reportlab': 'ReportLab (PDF)',
        'openpyxl': 'OpenPyXL (Excel)',
        'cryptography': 'Cryptography (Encriptación)',
        'requests': 'Requests'
    }
    
    all_installed = True
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print_success(f"{name}")
        except ImportError:
            print_error(f"{name} no instalado")
            all_installed = False
    
    if not all_installed:
        print_info("\nInstalar con: pip install -r billing_requirements.txt")
    
    return all_installed


def check_project_structure():
    """Verificar estructura del proyecto"""
    print_header("Verificación de Estructura del Proyecto")
    
    required_files = [
        'app/api/billing.py',
        'app/services/billing_service.py',
        'app/repositories/billing_repository.py',
        'app/schemas/billing.py',
        'app/utils/encryption.py',
        'app/api/webhooks.py',
    ]
    
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print_success(file)
        else:
            print_error(f"{file} no encontrado")
            all_exist = False
    
    return all_exist


def check_api_registration():
    """Verificar registro de routers en API"""
    print_header("Verificación de Registro de APIs")
    
    try:
        with open('app/api/__init__.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            routers = [
                ('billing_router', 'Billing Router'),
                ('webhooks_router', 'Webhooks Router')
            ]
            
            all_registered = True
            
            for router, name in routers:
                if router in content and f'include_router({router})' in content:
                    print_success(f"{name}")
                else:
                    print_error(f"{name} no registrado")
                    all_registered = False
            
            return all_registered
            
    except FileNotFoundError:
        print_error("app/api/__init__.py no encontrado")
        return False


def check_environment_variables():
    """Verificar variables de entorno"""
    print_header("Verificación de Variables de Entorno")
    
    try:
        from app.core.config import settings
        
        required_vars = [
            ('DATABASE_URL', 'URL de Base de Datos'),
            ('JWT_SECRET_KEY', 'Clave Secreta JWT'),
            ('MERCADOPAGO_CLIENT_ID', 'Client ID de MercadoPago'),
            ('MERCADOPAGO_CLIENT_SECRET', 'Client Secret de MercadoPago')
        ]
        
        all_configured = True
        
        for var, name in required_vars:
            if hasattr(settings, var) and getattr(settings, var):
                print_success(f"{name}")
            else:
                print_error(f"{name} no configurada")
                all_configured = False
        
        # Variables opcionales pero recomendadas
        optional_vars = [
            ('ENCRYPTION_KEY', 'Clave de Encriptación'),
            ('MERCADOPAGO_WEBHOOK_SECRET', 'Secret de Webhook MP')
        ]
        
        print_info("\nVariables opcionales:")
        for var, name in optional_vars:
            if hasattr(settings, var) and getattr(settings, var):
                print_success(f"{name}")
            else:
                print_warning(f"{name} no configurada (recomendado para producción)")
        
        return all_configured
        
    except ImportError:
        print_error("No se pudo importar settings")
        return False


def check_database_connection():
    """Verificar conexión a base de datos"""
    print_header("Verificación de Base de Datos")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            
        print_success("Conexión a base de datos exitosa")
        
        # Verificar tablas requeridas
        with engine.connect() as conn:
            tables = ['users', 'events', 'purchases', 'payments']
            all_exist = True
            
            print_info("\nTablas requeridas:")
            for table in tables:
                result = conn.execute(text(
                    f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
                ))
                exists = result.fetchone()[0]
                
                if exists:
                    print_success(f"Tabla '{table}'")
                else:
                    print_error(f"Tabla '{table}' no existe")
                    all_exist = False
            
            return all_exist
            
    except Exception as e:
        print_error(f"Error de conexión: {str(e)}")
        return False


def check_models():
    """Verificar modelos de datos"""
    print_header("Verificación de Modelos")
    
    try:
        from app.models.user import User
        from app.models.event import Event
        from app.models.purchase import Purchase
        from app.models.payment import Payment
        
        # Verificar campos de MercadoPago en User
        mp_fields = [
            'mercadopagoUserId',
            'mercadopagoAccessToken',
            'mercadopagoRefreshToken',
            'mercadopagoTokenExpires',
            'isMercadopagoConnected'
        ]
        
        all_exist = True
        print_info("Campos de MercadoPago en User:")
        for field in mp_fields:
            if hasattr(User, field):
                print_success(f"Campo '{field}'")
            else:
                print_error(f"Campo '{field}' no existe")
                all_exist = False
        
        return all_exist
        
    except ImportError as e:
        print_error(f"Error importando modelos: {str(e)}")
        return False


def check_encryption_system():
    """Verificar sistema de encriptación"""
    print_header("Verificación de Sistema de Encriptación")
    
    try:
        from app.utils.encryption import (
            encryption_service,
            encrypt_mercadopago_token,
            decrypt_mercadopago_token
        )
        
        # Probar encriptación/desencriptación
        test_data = "test_token_12345"
        
        encrypted = encrypt_mercadopago_token(test_data)
        decrypted = decrypt_mercadopago_token(encrypted)
        
        if decrypted == test_data:
            print_success("Sistema de encriptación funcionando correctamente")
            return True
        else:
            print_error("Sistema de encriptación tiene problemas")
            return False
            
    except Exception as e:
        print_error(f"Error en sistema de encriptación: {str(e)}")
        return False


def check_database_indexes():
    """Verificar índices de base de datos"""
    print_header("Verificación de Índices de Base de Datos")
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        indexes = [
            'idx_purchases_event_status',
            'idx_purchases_payment_date',
            'idx_purchases_created_at_desc',
            'idx_purchases_user_event',
            'idx_purchases_payment_reference',
            'idx_events_organizer',
            'idx_payments_transaction'
        ]
        
        with engine.connect() as conn:
            all_exist = True
            
            for index in indexes:
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = '{index}'
                    )
                """))
                exists = result.fetchone()[0]
                
                if exists:
                    print_success(f"Índice '{index}'")
                else:
                    print_warning(f"Índice '{index}' no existe (recomendado para performance)")
                    all_exist = False
            
            if not all_exist:
                print_info("\nCrear con: python create_billing_indexes.py")
            
            return all_exist
            
    except Exception as e:
        print_warning(f"No se pudieron verificar índices: {str(e)}")
        return False


def run_all_checks():
    """Ejecutar todas las verificaciones"""
    print(f"\n{BOLD}{GREEN}{'='*60}{ENDC}")
    print(f"{BOLD}{GREEN}Sistema de Facturación - Verificación Completa{ENDC}".center(70))
    print(f"{BOLD}{GREEN}{'='*60}{ENDC}\n")
    
    results = {
        'Python': check_python_version(),
        'Dependencias': check_dependencies(),
        'Estructura': check_project_structure(),
        'APIs': check_api_registration(),
        'Variables de Entorno': check_environment_variables(),
        'Base de Datos': check_database_connection(),
        'Modelos': check_models(),
        'Encriptación': check_encryption_system(),
        'Índices': check_database_indexes()
    }
    
    # Resumen final
    print_header("Resumen de Verificación")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        if result:
            print_success(f"{check}")
        else:
            print_error(f"{check}")
    
    print(f"\n{BOLD}Resultado: {passed}/{total} verificaciones exitosas{ENDC}\n")
    
    if passed == total:
        print(f"{BOLD}{GREEN}🎉 ¡Todos los componentes están correctamente configurados!{ENDC}")
        print(f"{GREEN}El sistema está listo para usar.{ENDC}\n")
        return True
    else:
        print(f"{BOLD}{YELLOW}⚠️  Algunos componentes requieren atención{ENDC}")
        print(f"{YELLOW}Revisa los errores arriba y corrige antes de continuar.{ENDC}\n")
        return False


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
