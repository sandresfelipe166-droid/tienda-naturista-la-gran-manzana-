from scripts.shared._utils import ensure_app_importable

ensure_app_importable()

from app.models.database import SessionLocal
from app.models.models import Rol


def main():
    db = SessionLocal()
    roles = db.query(Rol).all()
    print(f'Roles encontrados: {len(roles)}')
    for r in roles:
        print(f'  - {r.id_rol}: {r.nombre_rol}')
    db.close()


if __name__ == '__main__':
    main()
