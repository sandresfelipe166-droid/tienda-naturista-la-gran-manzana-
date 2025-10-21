import os
import sys
from typing import List

# Force sync driver normalization in app.models.database
os.environ["TESTING"] = "true"

# Ensure project root on sys.path when running from scripts/
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session

from app.core.roles import DEFAULT_ROLES
from app.models.database import Base, SessionLocal, engine
from app.models.models import Rol


def ensure_tables():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def list_roles(session: Session):
    roles = session.query(Rol).all()
    return [(r.id_rol, r.nombre_rol) for r in roles]


def seed_missing_roles(session: Session) -> list[str]:
    """Insert default roles that are missing. Returns names of inserted roles."""
    inserted = []
    existing_names = {r.nombre_rol for r in session.query(Rol).all()}
    for role_data in DEFAULT_ROLES:
        name = str(role_data.get("nombre_rol"))
        if name not in existing_names:
            r = Rol(
                nombre_rol=name,
                descripcion=role_data.get("descripcion", ""),
                permisos=role_data.get("permisos", ""),
            )
            session.add(r)
            inserted.append(name)
    if inserted:
        session.commit()
    return inserted


def main():
    ensure_tables()
    session = SessionLocal()
    try:
        before = list_roles(session)
        if not before:
            print("No se encontraron roles. Creando roles por defecto...")
        inserted = seed_missing_roles(session)
        after = list_roles(session)

        if inserted:
            print(f"Roles creados: {', '.join(inserted)}")
        else:
            if before:
                print("Ya existen roles; no fue necesario crear nuevos.")

        print("Roles existentes (id, nombre):")
        for rid, nombre in after:
            print(f"  - {rid}: {nombre}")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
