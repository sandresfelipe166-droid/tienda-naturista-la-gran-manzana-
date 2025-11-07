from datetime import datetime

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.models import Usuario
from app.models.schemas import UserCreate


def get_user_by_username(db: Session, username: str) -> Usuario | None:
    """Obtener usuario por username"""
    return db.query(Usuario).filter(Usuario.nombre_usuario == username).first()


def get_user_by_email(db: Session, email: str) -> Usuario | None:
    """Obtener usuario por email"""
    return db.query(Usuario).filter(Usuario.email == email).first()


def create_user(db: Session, user: UserCreate) -> Usuario:
    """Crear nuevo usuario"""
    hashed_password = get_password_hash(user.password)
    db_user = Usuario(
        nombre_usuario=user.username,
        email=user.email,
        password_hash=hashed_password,
        nombre_completo=user.nombre_completo,
        id_rol=user.rol_id,
        estado="Activo",
        fecha_creacion=datetime.utcnow(),
        ultima_acceso=None,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtener lista de usuarios"""
    return db.query(Usuario).offset(skip).limit(limit).all()


def authenticate_user(db: Session, username: str, password: str):
    """Autenticar usuario"""
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):  # type: ignore[arg-type]
        return False
    return user


def update_user(db: Session, user_id: int, user_data: dict) -> Usuario | None:
    """Actualizar usuario"""
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        return None

    # Verificar si el nuevo username ya existe (si se cambia)
    if 'nombre_usuario' in user_data and user_data['nombre_usuario'] != user.nombre_usuario:
        if get_user_by_username(db, user_data['nombre_usuario']):
            raise ValueError("Username already taken")

    # Verificar si el nuevo email ya existe (si se cambia)
    if 'email' in user_data and user_data['email'] != user.email:
        if get_user_by_email(db, user_data['email']):
            raise ValueError("Email already registered")

    # Actualizar campos
    for key, value in user_data.items():
        if key == 'password':
            value = get_password_hash(value)
            user.password_hash = value  # type: ignore[assignment]
        elif key == 'username':
            user.nombre_usuario = value  # type: ignore[assignment]
        elif key == 'id_rol':
            user.id_rol = value  # type: ignore[assignment]
        elif hasattr(user, key):
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, logical: bool = True) -> bool:
    """Eliminar usuario (lógico o físico)"""
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        return False

    if logical:
        user.estado = "Inactivo"  # type: ignore[assignment]
        db.commit()
    else:
        db.delete(user)
        db.commit()

    return True
