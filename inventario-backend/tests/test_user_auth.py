import os
import uuid
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Set testing environment variable to use sync database driver BEFORE importing app
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient

from app.models.database import Base, engine, get_db
from main import app

Base.metadata.create_all(bind=engine)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.roles import DEFAULT_ROLES, Role
from app.core.security import create_access_token
from app.models.models import Rol, Usuario

# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Mock database session to avoid real DB calls
@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_db():
    db = MagicMock()
    return db


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# Apply dependency override for get_db across all tests in this module
@pytest.fixture(scope="function", autouse=True)
def override_get_db(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


# --- Test Client ---
@pytest.fixture(scope="module")
def client():
    # Remove auth overrides to test real authentication
    from app.core.auth_middleware import get_current_active_user

    app.dependency_overrides.pop(get_current_active_user, None)
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def seed_roles(db_engine):
    """Seed default roles before tests run."""
    db = TestingSessionLocal()
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
    finally:
        db.close()


class MockRole:
    def __init__(self, nombre_rol="admin"):
        self.id_rol = 1
        self.nombre_rol = nombre_rol


class MockUser:
    def __init__(self, nombre_usuario="testuser"):
        self.id_usuario = 1
        self.nombre_usuario = nombre_usuario
        self.email = "test@example.com"
        self.nombre_completo = "Test User"
        self.estado = "Activo"
        self.rol = MockRole()
        self.password_hash = "hashed"
        self.id_rol = 1
        self.fecha_creacion = None
        self.ultima_acceso = None


def get_auth_headers(username: str, role: str) -> dict:
    token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    return get_auth_headers("admin_user", Role.ADMIN.value)


@pytest.fixture
def normal_headers():
    return get_auth_headers("normal_user", Role.USER.value)


def test_register_user_success(client):
    unique_id = uuid.uuid4().hex[:8]
    username = f"newuser_{unique_id}"
    email = f"{username}@example.com"
    payload = {"username": username, "email": email, "password": "strongpassword", "rol_id": 1}
    # Clean up any existing user
    db = TestingSessionLocal()
    try:
        existing_user = (
            db.query(Usuario)
            .filter((Usuario.nombre_usuario == username) | (Usuario.email == email))
            .first()
        )
        if existing_user:
            db.delete(existing_user)
            db.commit()
    finally:
        db.close()

    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["nombre_usuario"] == username
    assert "id_usuario" in data


def test_login_user_success(client):
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        mock_auth.return_value = MockUser()
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "testuser", "password": "testpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


def test_login_user_failure(client):
    with patch("app.routers.auth.authenticate_user") as mock_auth:
        mock_auth.return_value = None
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "wronguser", "password": "wrongpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "Incorrect username or password"


def test_get_current_user(client, admin_headers):
    with patch("app.routers.auth.get_user_by_username") as mock_get_user:
        mock_get_user.return_value = MockUser()
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["nombre_usuario"] == "testuser"


def test_protected_route_requires_auth(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401  # Unauthorized without token


def test_access_users_with_valid_token(client, admin_headers):
    with (
        patch("app.core.auth_middleware.get_current_user_from_token") as mock_get_user,
        patch("app.routers.users.get_users") as mock_get_users,
    ):
        mock_get_user.return_value = MockUser()
        mock_get_users.return_value = [MockUser()]
        response = client.get("/api/v1/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
