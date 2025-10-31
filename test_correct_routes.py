# -*- coding: utf-8 -*-
"""
Script para probar el endpoint de búsqueda con las rutas correctas
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_endpoint(url, description):
    """Probar un endpoint y mostrar respuesta"""
    print(f"\n{'='*80}")
    print(f"🔍 {description}")
    print(f"📍 URL: {url}")
    print(f"{'='*80}\n")
    
    try:
        response = requests.get(url)
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Mostrar estructura
            if isinstance(data, dict):
                print(f"\n📦 Estructura: {type(data).__name__}")
                print(f"   Claves: {list(data.keys())}")
                
                if 'events' in data:
                    print(f"   📊 Total eventos: {data.get('total', 0)}")
                    print(f"   📄 Eventos en página: {len(data.get('events', []))}")
                    
                    if data.get('events'):
                        event = data['events'][0]
                        print(f"\n   📋 Primer evento:")
                        print(f"      • ID: {event.get('id', 'N/A')}")
                        print(f"      • Título: {event.get('title', 'N/A')}")
                        print(f"      • Venue: {event.get('venue', 'N/A')}")
                        print(f"      • Precio mín: {event.get('minPrice', 'N/A')}")
                        if event.get('category'):
                            print(f"      • Categoría: {event.get('category', {}).get('name', 'N/A')}")
            
            elif isinstance(data, list):
                print(f"\n📦 Estructura: Array de {len(data)} eventos")
                
                if data:
                    event = data[0]
                    print(f"\n   📋 Primer evento:")
                    print(f"      • ID: {event.get('id', 'N/A')}")
                    print(f"      • Título: {event.get('title', 'N/A')}")
                    print(f"      • Venue: {event.get('venue', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al backend")
        print("   ¿Está corriendo el servidor en http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Probar diferentes endpoints"""
    print("\n" + "="*80)
    print("🧪 TEST DE ENDPOINTS DE BÚSQUEDA - RUTAS CORREGIDAS")
    print("="*80)
    
    # Test 1: Root
    test_endpoint(
        f"{API_URL}/",
        "0️⃣  Root endpoint"
    )
    
    # Test 2: Listar todos los eventos - /api/events
    test_endpoint(
        f"{API_URL}/api/events",
        "1️⃣  Listar todos los eventos (ruta correcta: /api/events)"
    )
    
    # Test 3: Búsqueda sin parámetros
    test_endpoint(
        f"{API_URL}/api/events/search",
        "2️⃣  Endpoint de búsqueda sin parámetros"
    )
    
    # Test 4: Búsqueda por categoría
    test_endpoint(
        f"{API_URL}/api/events/search?categories=conciertos",
        "3️⃣  Búsqueda por categoría (conciertos)"
    )
    
    # Test 5: Búsqueda por ubicación
    test_endpoint(
        f"{API_URL}/api/events/search?location=Lima",
        "4️⃣  Búsqueda por ubicación (Lima)"
    )
    
    print("\n" + "="*80)
    print("✅ Tests completados")
    print("\n💡 La ruta correcta es: /api/events (NO /api/v1/events)")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
