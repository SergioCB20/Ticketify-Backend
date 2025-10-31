# -*- coding: utf-8 -*-
"""
Script para probar el endpoint de búsqueda
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
                        print(f"      • Categoría: {event.get('category', {}).get('name', 'N/A')}")
                        print(f"\n   🔑 Todas las claves del evento:")
                        print(f"      {list(event.keys())}")
            
            elif isinstance(data, list):
                print(f"\n📦 Estructura: Array de {len(data)} eventos")
                
                if data:
                    event = data[0]
                    print(f"\n   📋 Primer evento:")
                    print(f"      • ID: {event.get('id', 'N/A')}")
                    print(f"      • Título: {event.get('title', 'N/A')}")
                    print(f"      • Venue: {event.get('venue', 'N/A')}")
                    print(f"      • Precio: {event.get('price', event.get('minPrice', 'N/A'))}")
                    print(f"\n   🔑 Todas las claves del evento:")
                    print(f"      {list(event.keys())}")
            
            # Mostrar JSON completo (solo primeros 2 elementos si es array)
            print(f"\n📄 JSON completo:")
            if isinstance(data, list) and len(data) > 2:
                print(json.dumps(data[:2], indent=2, ensure_ascii=False))
                print(f"   ... y {len(data) - 2} eventos más")
            else:
                print(json.dumps(data, indent=2, ensure_ascii=False))
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
    print("🧪 TEST DE ENDPOINTS DE BÚSQUEDA")
    print("="*80)
    
    # Test 1: Listar todos los eventos
    test_endpoint(
        f"{API_URL}/api/v1/events",
        "1️⃣  Listar todos los eventos (sin filtros)"
    )
    
    # Test 2: Búsqueda sin parámetros
    test_endpoint(
        f"{API_URL}/api/v1/events/search",
        "2️⃣  Endpoint de búsqueda sin parámetros"
    )
    
    # Test 3: Búsqueda por categoría
    test_endpoint(
        f"{API_URL}/api/v1/events/search?categories=conciertos",
        "3️⃣  Búsqueda por categoría (conciertos)"
    )
    
    # Test 4: Búsqueda por ubicación
    test_endpoint(
        f"{API_URL}/api/v1/events/search?location=Lima",
        "4️⃣  Búsqueda por ubicación (Lima)"
    )
    
    # Test 5: Búsqueda por precio
    test_endpoint(
        f"{API_URL}/api/v1/events/search?min_price=0&max_price=100",
        "5️⃣  Búsqueda por precio (0-100)"
    )
    
    print("\n" + "="*80)
    print("✅ Tests completados")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
