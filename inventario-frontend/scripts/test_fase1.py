"""
Script de prueba rápida para las mejoras de Fase 1
"""

import json
from datetime import datetime

import requests

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")


def test_endpoint(name, url, method="GET", data=None, headers=None):
    """Probar un endpoint"""
    print_info(f"Probando: {name}")
    response = None
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=5)
        else:
            print_error(f"{name} - Método HTTP no soportado: {method}")
            return None

        if response and response.status_code in [200, 201]:
            print_success(f"{name} - Status: {response.status_code}")
            return response.json()
        elif response:
            print_error(f"{name} - Status: {response.status_code}")
            return None
        else:
            print_error(f"{name} - No se obtuvo respuesta")
            return None
    except requests.exceptions.ConnectionError:
        print_error(f"{name} - No se pudo conectar al servidor")
        print_warning("Asegúrate de que el servidor esté corriendo: uvicorn main:app --reload")
        return None
    except Exception as e:
        print_error(f"{name} - Error: {str(e)}")
        return None


def main():
    print("\n" + "=" * 60)
    print(f"{BLUE}🚀 PRUEBA DE FASE 1 - MEJORAS IMPLEMENTADAS{RESET}")
    print("=" * 60 + "\n")

    # 1. Verificar servidor
    print_info("1. Verificando servidor...")
    result = test_endpoint("Health Check", f"{API_URL}/health")
    if not result:
        print_error("El servidor no está disponible. Abortando pruebas.")
        return
    print()

    # 2. Obtener token (necesario para endpoints protegidos)
    print_info("2. Obteniendo token de autenticación...")
    print_warning("Nota: Necesitas un usuario creado. Si falla, crea uno primero.")

    # Intentar login (ajusta credenciales según tu BD)
    login_data = {"username": "admin", "password": "admin123"}

    login_response = requests.post(f"{API_URL}/auth/login", data=login_data, timeout=5)

    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print_success("Token obtenido exitosamente")
    else:
        print_warning("No se pudo obtener token. Algunos endpoints fallarán.")
        headers = {}
    print()

    # 3. Probar búsqueda avanzada
    print_info("3. Probando búsqueda avanzada con filtros...")
    result = test_endpoint(
        "Búsqueda Avanzada",
        f"{API_URL}/productos/advanced?page=1&size=10&estado=Activo",
        headers=headers,
    )
    if result and 'pagination' in result:
        print_success(f"   Paginación funcionando: {result['pagination']}")
    print()

    # 4. Probar búsqueda por término
    print_info("4. Probando búsqueda por término...")
    result = test_endpoint(
        "Búsqueda por Término", f"{API_URL}/productos/search?q=test&page=1&size=10", headers=headers
    )
    print()

    # 5. Probar estadísticas
    print_info("5. Probando estadísticas de productos...")
    result = test_endpoint("Estadísticas", f"{API_URL}/productos/stats", headers=headers)
    if result and 'data' in result:
        stats = result['data']
        print_success(f"   Total productos: {stats.get('total_productos', 'N/A')}")
        print_success(f"   Valor inventario: ${stats.get('valor_total_inventario', 0):.2f}")
        print_success(f"   Stock bajo: {stats.get('productos_bajo_stock', 'N/A')}")
    print()

    # 6. Probar top productos
    print_info("6. Probando top productos...")
    result = test_endpoint(
        "Top Productos", f"{API_URL}/productos/top?limit=5&criterio=stock", headers=headers
    )
    print()

    # 7. Probar stats por laboratorio
    print_info("7. Probando estadísticas por laboratorio...")
    result = test_endpoint(
        "Stats por Laboratorio", f"{API_URL}/productos/stats/por-laboratorio", headers=headers
    )
    print()

    # 8. Probar stats por sección
    print_info("8. Probando estadísticas por sección...")
    result = test_endpoint(
        "Stats por Sección", f"{API_URL}/productos/stats/por-seccion", headers=headers
    )
    print()

    # 9. Probar estadísticas de caché
    print_info("9. Probando estadísticas de caché Redis...")
    result = test_endpoint("Cache Stats", f"{API_URL}/productos/cache/stats", headers=headers)
    if result and 'data' in result:
        cache_data = result['data']
        if cache_data.get('enabled'):
            print_success(f"   Redis habilitado")
            print_success(f"   Total keys: {cache_data.get('total_keys', 0)}")
            print_success(f"   Hit rate: {cache_data.get('hit_rate', 0):.2f}%")
        else:
            print_warning("   Redis no está habilitado o no está disponible")
    print()

    # 10. Verificar caché funcionando
    print_info("10. Verificando funcionamiento del caché...")
    print_info("    Primera llamada (debe ser MISS)...")
    start = datetime.now()
    result1 = test_endpoint("Cache Test 1", f"{API_URL}/productos/stats", headers=headers)
    time1 = (datetime.now() - start).total_seconds() * 1000

    print_info("    Segunda llamada (debe ser HIT)...")
    start = datetime.now()
    result2 = test_endpoint("Cache Test 2", f"{API_URL}/productos/stats", headers=headers)
    time2 = (datetime.now() - start).total_seconds() * 1000

    if result1 and result2:
        print_success(f"   Primera llamada: {time1:.0f}ms")
        print_success(f"   Segunda llamada: {time2:.0f}ms")
        if time2 < time1:
            speedup = time1 / time2
            print_success(f"   Mejora de velocidad: {speedup:.1f}x más rápido")
        else:
            print_warning("   El caché podría no estar funcionando correctamente")
    print()

    # Resumen final
    print("\n" + "=" * 60)
    print(f"{GREEN}✅ PRUEBAS COMPLETADAS{RESET}")
    print("=" * 60)
    print(f"\n{BLUE}Próximos pasos:{RESET}")
    print("1. Revisa los logs en logs/inventario.log")
    print("2. Explora la documentación en http://localhost:8000/docs")
    print("3. Busca la sección 'productos-advanced' en Swagger")
    print("4. Prueba diferentes combinaciones de filtros")
    print("\n")


if __name__ == "__main__":
    main()
