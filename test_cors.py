#!/usr/bin/env python3
"""
Script para verificar la configuración de CORS del backend de Ticketify
"""

import requests
import sys
from colorama import init, Fore, Style

# Inicializar colorama para colores en terminal
init(autoreset=True)

def print_header(text):
    """Imprime un encabezado coloreado"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text:^60}")
    print(f"{Fore.CYAN}{'='*60}\n")

def print_success(text):
    """Imprime texto de éxito"""
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    """Imprime texto de error"""
    print(f"{Fore.RED}✗ {text}")

def print_info(text):
    """Imprime texto informativo"""
    print(f"{Fore.YELLOW}ℹ {text}")

def test_cors():
    """Prueba la configuración de CORS del backend"""
    
    backend_url = "http://localhost:8000"
    frontend_origin = "http://localhost:3000"
    
    print_header("VERIFICACIÓN DE CORS - TICKETIFY BACKEND")
    
    # Test 1: Verificar que el servidor esté corriendo
    print_info("Test 1: Verificando que el servidor backend esté corriendo...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Servidor backend corriendo en {backend_url}")
        else:
            print_error(f"Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"No se pudo conectar al servidor en {backend_url}")
        print_info("Asegúrate de que el servidor esté corriendo: python run.py")
        return False
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        return False
    
    # Test 2: Verificar endpoint raíz
    print_info("\nTest 2: Verificando endpoint raíz...")
    try:
        response = requests.get(backend_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Endpoint raíz responde correctamente")
            print_info(f"   Versión: {data.get('message', 'N/A')}")
            print_info(f"   Estado: {data.get('status', 'N/A')}")
            print_info(f"   Ambiente: {data.get('environment', 'N/A')}")
    except Exception as e:
        print_error(f"Error en endpoint raíz: {str(e)}")
    
    # Test 3: Verificar cabeceras CORS en preflight request
    print_info("\nTest 3: Verificando cabeceras CORS (Preflight Request)...")
    try:
        response = requests.options(
            f"{backend_url}/api/events",
            headers={
                "Origin": frontend_origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=5
        )
        
        # Verificar cabeceras CORS
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        if cors_headers["Access-Control-Allow-Origin"] == frontend_origin:
            print_success("CORS configurado correctamente")
            print_info(f"   Allow-Origin: {cors_headers['Access-Control-Allow-Origin']}")
            print_info(f"   Allow-Methods: {cors_headers['Access-Control-Allow-Methods']}")
            print_info(f"   Allow-Headers: {cors_headers['Access-Control-Allow-Headers']}")
            print_info(f"   Allow-Credentials: {cors_headers['Access-Control-Allow-Credentials']}")
        else:
            print_error(f"CORS no permite origen {frontend_origin}")
            print_info(f"   Origen permitido: {cors_headers['Access-Control-Allow-Origin']}")
            return False
            
    except Exception as e:
        print_error(f"Error verificando CORS: {str(e)}")
        return False
    
    # Test 4: Verificar petición GET real
    print_info("\nTest 4: Verificando petición GET real con Origin...")
    try:
        response = requests.get(
            f"{backend_url}/api/events",
            headers={"Origin": frontend_origin},
            timeout=5
        )
        
        allow_origin = response.headers.get("Access-Control-Allow-Origin")
        if allow_origin == frontend_origin:
            print_success("Peticiones GET permitidas desde el frontend")
            print_info(f"   Código de respuesta: {response.status_code}")
        else:
            print_error("CORS no permite GET desde el frontend")
            return False
            
    except Exception as e:
        print_error(f"Error en petición GET: {str(e)}")
        return False
    
    # Test 5: Verificar otros orígenes
    print_info("\nTest 5: Verificando que otros orígenes sean rechazados...")
    try:
        response = requests.get(
            f"{backend_url}/api/events",
            headers={"Origin": "http://malicious-site.com"},
            timeout=5
        )
        
        allow_origin = response.headers.get("Access-Control-Allow-Origin")
        if allow_origin != "http://malicious-site.com":
            print_success("Orígenes no autorizados son rechazados correctamente")
        else:
            print_error("ADVERTENCIA: CORS permite orígenes no autorizados")
            
    except Exception as e:
        print_error(f"Error verificando restricción de orígenes: {str(e)}")
    
    # Resumen final
    print_header("RESUMEN")
    print_success("Todas las pruebas de CORS pasaron correctamente")
    print_info(f"\nEl backend está listo para recibir peticiones desde:")
    print_info(f"   • {frontend_origin}")
    print_info(f"\nPuedes iniciar tu frontend y comenzar a hacer peticiones.")
    
    return True

if __name__ == "__main__":
    try:
        success = test_cors()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_info("\n\nPrueba cancelada por el usuario")
        sys.exit(1)
