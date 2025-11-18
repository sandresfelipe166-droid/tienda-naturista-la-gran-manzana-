"""Comprobación rápida de la BD remota y Alembic.

Ejecuta este script en el entorno del proyecto (venv activado) y con
la variable de entorno `DATABASE_URL` apuntando a la base de datos que
quieres inspeccionar (por ejemplo la de Render). El script hace:
- imprime la DB y esquema actuales
- consulta existencia y conteo de la tabla `rol`
- consulta la fila en `alembic_version`
- ejecuta `alembic current` para mostrar la revisión que Alembic ve

Uso (PowerShell):
  $env:DATABASE_URL = "postgresql://<USER>:<PASS>@<HOST>:<PORT>/<DB>"
  python .\inventario-backend\scripts\check_prod_db.py

No se imprimen credenciales; asegúrate de usar este script en consola
privada.
"""
from __future__ import annotations

import os
import sys
import subprocess
from typing import Any

import sqlalchemy as sa


def run_alembic_current(cwd: str) -> str:
    """Run `python -m alembic -c alembic.ini current` and return output."""
    try:
        cmd = [sys.executable, "-m", "alembic", "-c", "alembic.ini", "current"]
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        out = res.stdout.strip()
        err = res.stderr.strip()
        if res.returncode != 0:
            return f"(alembic current failed, rc={res.returncode})\nSTDOUT:\n{out}\nSTDERR:\n{err}"
        return out if out else "(alembic current produced no stdout)"
    except Exception as e:
        return f"(alembic current error: {e})"


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: setea la variable de entorno DATABASE_URL antes de ejecutar.")
        return 2

    backend_dir = os.path.join(os.getcwd(), "inventario-backend")

    print("Usando DATABASE_URL (mascarizado):")
    # Mask credentials for safety in logs
    try:
        parsed = sa.engine.make_url(database_url)
        print(f"  dialect+driver: {parsed.drivername}")
        print(f"  host: {parsed.host}")
        print(f"  port: {parsed.port}")
        print(f"  database: {parsed.database}")
    except Exception:
        print("  (no se pudo parsear DATABASE_URL)")

    # Run alembic current
    print("\n=== alembic current (ejecutando) ===")
    print(run_alembic_current(backend_dir))

    # Connect with SQLAlchemy and run some checks
    engine = sa.create_engine(database_url)
    with engine.connect() as conn:
        print("\n=== DB checks via SQL ===")
        try:
            res = conn.execute(sa.text("select current_database(), current_schema()"))
            print("current_database(), current_schema():", res.fetchall())
        except Exception as e:
            print("Error al obtener current_database/current_schema:", e)

        # Check alembic_version table
        try:
            res = conn.execute(sa.text("select version_num from alembic_version"))
            rows = res.fetchall()
            print("alembic_version rows:", rows)
        except Exception as e:
            print("alembic_version query error:", e)

        # Check rol table existence and count
        try:
            res = conn.execute(sa.text("select count(*) from rol"))
            cnt = res.scalar()
            print("rol row count:", cnt)
        except Exception as e:
            print("rol table query error (posible non-existence):", e)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
