import os
import sys

# Asegura que el proyecto esté en el path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user_by_email, get_user_by_username
from app.models.database import Base, SessionLocal, engine
from app.models.schemas import UserCreate


def ensure_tables():
    Base.metadata.create_all(bind=engine)


def seed_admin_user():
    session = SessionLocal()
    try:
        ensure_tables()
        username = "felipe"
        email = "felipe@gmail.com"
        password = "123456789"
        rol_id = 1
        nombre_completo = "Felipe Admin"
        # Verifica si ya existe
        if get_user_by_username(session, username) or get_user_by_email(session, email):
            print("El usuario ya existe. No se creó uno nuevo.")
            return
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            rol_id=rol_id,
            nombre_completo=nombre_completo,
        )
        user = create_user(session, user_data)
        print(f"Usuario creado: {user.nombre_usuario} ({user.email}) con rol_id {user.id_rol}")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    seed_admin_user()
