"""
Health Check Script - Validación de servicios críticos

Este script valida que todos los servicios estén funcionando correctamente:
- Backend API (FastAPI)
- Base de datos (PostgreSQL)
- Redis Cache
- Permisos y conectividad

Uso:
    python scripts/health_check.py
    python scripts/health_check.py --detailed
    python scripts/health_check.py --api-url http://localhost:8000

Retorna:
    0: Todos los servicios OK
    1: Algún servicio falló

Requisitos:
    pip install requests psycopg2-binary redis rich
"""

import argparse
import sys
import time
from typing import Dict, List, Tuple

try:
    import psycopg2
except ImportError:
    print("⚠️  psycopg2-binary no está instalado")
    psycopg2 = None

try:
    import redis
except ImportError:
    print("⚠️  redis no está instalado")
    redis = None

try:
    import requests
except ImportError:
    print("⚠️  requests no está instalado")
    requests = None

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("⚠️  rich no está instalado, usando output simple")
    Console = None
    Table = None

console = Console() if Console else None


def check_api_health(api_url: str, timeout: int = 5) -> Tuple[bool, str]:
    """Verificar salud del API"""
    if not requests:
        return False, "❌ requests no está instalado"
    try:
        response = requests.get(f"{api_url}/api/v1/health", timeout=timeout)
        if response.status_code == 200:
            return True, "✅ API respondiendo correctamente"
        else:
            return False, f"❌ API retornó status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "❌ No se puede conectar al API"
    except requests.exceptions.Timeout:
        return False, f"❌ API timeout ({timeout}s)"
    except Exception as e:
        return False, f"❌ Error inesperado: {str(e)}"


def check_api_detailed_health(api_url: str, timeout: int = 5) -> Tuple[bool, Dict]:
    """Verificar salud detallada del API"""
    try:
        response = requests.get(f"{api_url}/api/v1/health/detailed", timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, {"error": f"Status {response.status_code}"}
    except Exception as e:
        return False, {"error": str(e)}


def check_database_direct(
    host: str = "localhost",
    port: int = 5432,
    database: str = "inventario",
    user: str = "admin",
    password: str = "admin123",
) -> Tuple[bool, str]:
    """Verificar conexión directa a PostgreSQL"""
    if not psycopg2:
        return False, "❌ psycopg2 no está instalado"
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return True, f"✅ PostgreSQL conectado: {version[:50]}..."
    except psycopg2.OperationalError as e:
        return False, f"❌ Error de conexión PostgreSQL: {str(e)[:100]}"
    except Exception as e:
        return False, f"❌ Error inesperado: {str(e)}"


def check_redis_direct(
    host: str = "localhost", port: int = 6379, db: int = 0, timeout: int = 5
) -> Tuple[bool, str]:
    """Verificar conexión directa a Redis"""
    if not redis:
        return False, "❌ redis no está instalado"
    try:
        r = redis.Redis(
            host=host, port=port, db=db, socket_timeout=timeout, decode_responses=True
        )
        r.ping()
        info = r.info("server")
        version = info.get("redis_version", "unknown")
        r.close()
        return True, f"✅ Redis conectado: v{version}"
    except redis.ConnectionError:
        return False, "❌ No se puede conectar a Redis"
    except redis.TimeoutError:
        return False, f"❌ Redis timeout ({timeout}s)"
    except Exception as e:
        return False, f"❌ Error inesperado: {str(e)}"


def check_api_endpoints(api_url: str) -> List[Tuple[str, bool, str]]:
    """Verificar endpoints críticos del API"""
    endpoints = [
        ("/api/v1/health", "Health Check"),
        ("/api/v1/health/detailed", "Health Detailed"),
        ("/api/v1/health/metrics", "Metrics"),
        ("/docs", "API Documentation"),
    ]

    results = []
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{api_url}{endpoint}", timeout=3)
            if response.status_code == 200:
                results.append((name, True, f"✅ {response.status_code}"))
            else:
                results.append((name, False, f"❌ {response.status_code}"))
        except Exception as e:
            results.append((name, False, f"❌ {str(e)[:50]}"))

    return results


def run_health_check(api_url: str, detailed: bool = False) -> int:
    """Ejecutar health check completo"""
    if console:
        console.print("\n[bold cyan]🏥 Health Check - Sistema de Inventario[/bold cyan]\n")
    else:
        print("\n🏥 Health Check - Sistema de Inventario\n")

    results = {}
    all_ok = True

    # 1. API Health
    if console:
        with console.status("[bold green]Verificando API..."):
            ok, msg = check_api_health(api_url)
            results["API"] = (ok, msg)
            all_ok = all_ok and ok
            time.sleep(0.5)
    else:
        print("Verificando API...")
        ok, msg = check_api_health(api_url)
        results["API"] = (ok, msg)
        all_ok = all_ok and ok

    # 2. Database
    if console:
        with console.status("[bold green]Verificando PostgreSQL..."):
            ok, msg = check_database_direct()
            results["Database"] = (ok, msg)
            all_ok = all_ok and ok
            time.sleep(0.5)
    else:
        print("Verificando PostgreSQL...")
        ok, msg = check_database_direct()
        results["Database"] = (ok, msg)
        all_ok = all_ok and ok

    # 3. Redis
    if console:
        with console.status("[bold green]Verificando Redis..."):
            ok, msg = check_redis_direct()
            results["Redis"] = (ok, msg)
            all_ok = all_ok and ok
            time.sleep(0.5)
    else:
        print("Verificando Redis...")
        ok, msg = check_redis_direct()
        results["Redis"] = (ok, msg)
        all_ok = all_ok and ok

    # Mostrar resultados básicos
    if console and Table:
        table = Table(title="Resumen de Servicios")
        table.add_column("Servicio", style="cyan", no_wrap=True)
        table.add_column("Estado", style="magenta")

        for service, (ok, msg) in results.items():
            table.add_row(service, msg)

        console.print(table)
    else:
        print("\nResumen de Servicios:")
        for service, (ok, msg) in results.items():
            print(f"  {service}: {msg}")

    # Verificación detallada si se solicita
    if detailed:
        console.print("\n[bold yellow]📊 Health Check Detallado[/bold yellow]\n")

        # API Detailed Health
        ok, data = check_api_detailed_health(api_url)
        if ok:
            console.print("[green]✅ API Detailed Health:[/green]")
            console.print(f"  Status: {data.get('status', 'unknown')}")
            console.print(f"  Environment: {data.get('environment', 'unknown')}")
            console.print(f"  Database: {data.get('database', {}).get('status', 'unknown')}")
            console.print(f"  Redis: {data.get('redis', {}).get('status', 'unknown')}")
        else:
            console.print("[red]❌ No se pudo obtener health detallado[/red]")

        # Endpoints
        console.print("\n[bold yellow]🔍 Verificación de Endpoints:[/bold yellow]\n")
        endpoint_results = check_api_endpoints(api_url)

        endpoint_table = Table()
        endpoint_table.add_column("Endpoint", style="cyan")
        endpoint_table.add_column("Estado", style="magenta")

        for name, ok, status in endpoint_results:
            endpoint_table.add_row(name, status)

        console.print(endpoint_table)

    # Resultado final
    console.print()
    if all_ok:
        console.print("[bold green]✅ Todos los servicios están funcionando correctamente[/bold green]")
        return 0
    else:
        console.print("[bold red]❌ Algunos servicios presentan problemas[/bold red]")
        console.print("[yellow]💡 Sugerencias:[/yellow]")
        console.print("  1. Verificar que Docker Compose esté corriendo: docker-compose ps")
        console.print("  2. Verificar logs: docker-compose logs -f")
        console.print("  3. Reiniciar servicios: docker-compose restart")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Health Check - Sistema de Inventario")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8000",
        help="URL del API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--detailed", action="store_true", help="Mostrar información detallada"
    )

    args = parser.parse_args()

    try:
        exit_code = run_health_check(args.api_url, args.detailed)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Health check interrumpido por el usuario[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]❌ Error fatal: {str(e)}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
