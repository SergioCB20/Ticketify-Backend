#!/usr/bin/env python3
"""
Script mejorado para iniciar el backend de Ticketify con verificación de configuración
"""

import sys
import os
import subprocess
from pathlib import Path

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def check_env_file():
    """Verifica que exista el archivo .env"""
    if not Path('.env').exists():
        print_error("No se encontró el archivo .env")
        print_info("Copia .env.example a .env y configúralo:")
        print_info("  cp .env.example .env")
        return False
    print_success("Archivo .env encontrado")
    return True

def check_cors_config():
    """Verifica la configuración de CORS"""
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'ALLOWED_HOSTS' in content:
                # Extraer configuración
                for line in content.split('\n'):
                    if line.startswith('ALLOWED_HOSTS'):
                        print_success("Configuración CORS encontrada")
                        print_info(f"  {line}")
                        return True
        print_warning("No se encontró configuración de ALLOWED_HOSTS")
        return False
    except Exception as e:
        print_error(f"Error leyendo .env: {e}")
        return False

def check_database_url():
    """Verifica la URL de la base de datos"""
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'DATABASE_URL' in content:
                print_success("Configuración de base de datos encontrada")
                return True
        print_warning("No se encontró DATABASE_URL en .env")
        return False
    except Exception as e:
        print_error(f"Error verificando base de datos: {e}")
        return False

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Se requiere Python 3.10+")
        return False

def check_dependencies():
    """Verifica que estén instaladas las dependencias principales"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print_success("Dependencias principales instaladas")
        return True
    except ImportError as e:
        print_error(f"Faltan dependencias: {e}")
        print_info("Instala las dependencias con: pip install -r requirements.txt")
        return False

def main():
    """Función principal"""
    print_header("TICKETIFY BACKEND - INICIALIZACIÓN")
    
    # Verificaciones previas
    print_info("Verificando configuración...")
    
    checks = [
        ("Versión de Python", check_python_version()),
        ("Dependencias", check_dependencies()),
        ("Archivo .env", check_env_file()),
        ("Configuración CORS", check_cors_config()),
        ("Base de datos", check_database_url()),
    ]
    
    failed_checks = [name for name, result in checks if not result]
    
    if failed_checks:
        print_error("\nVerificaciones fallidas:")
        for name in failed_checks:
            print_error(f"  • {name}")
        print_info("\nPor favor, corrige los errores antes de continuar.")
        return 1
    
    print_success("\n✓ Todas las verificaciones pasaron")
    
    # Información de inicio
    print_header("INFORMACIÓN DEL SERVIDOR")
    print_info("URL del servidor: http://localhost:8000")
    print_info("Documentación API: http://localhost:8000/docs")
    print_info("ReDoc: http://localhost:8000/redoc")
    print_info("Health Check: http://localhost:8000/health")
    
    print_info("\nOrígenes CORS permitidos:")
    print_info("  • http://localhost:3000")
    print_info("  • http://localhost:3001")
    
    print_header("INICIANDO SERVIDOR")
    print_info("Presiona Ctrl+C para detener el servidor\n")
    
    try:
        # Iniciar el servidor
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print_info("\n\nServidor detenido por el usuario")
        return 0
    except Exception as e:
        print_error(f"\nError al iniciar el servidor: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
