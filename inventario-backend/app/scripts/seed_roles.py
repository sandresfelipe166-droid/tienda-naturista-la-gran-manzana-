"""Seed default roles into the database.

This script is idempotent and intended to be executed after migrations
have been applied (for example from the container entrypoint).
"""
from __future__ import annotations

from typing import List
import sys

from app.models.database import SessionLocal
from app.models.models import Rol
from app.core.roles import DEFAULT_ROLES


def seed_roles() -> List[str]:
    db = SessionLocal()
    inserted: List[str] = []
    try:
        existing = {r.nombre_rol for r in db.query(Rol).all()}
        to_insert = []
        for role in DEFAULT_ROLES:
            name = str(role.get("nombre_rol"))
            if name not in existing:
                to_insert.append(
                    Rol(
                        nombre_rol=name,
                        descripcion=role.get("descripcion", ""),
                        permisos=role.get("permisos", ""),
                    )
                )
        if to_insert:
            db.add_all(to_insert)
            db.commit()
            inserted = [r.nombre_rol for r in to_insert]
    finally:
        db.close()
    return inserted


def main() -> int:
    try:
        inserted = seed_roles()
        if inserted:
            print(f"Seeded roles: {inserted}")
        else:
            print("Default roles already present (no action taken)")
        return 0
    except Exception as e:
        print(f"Role seeding failed: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
