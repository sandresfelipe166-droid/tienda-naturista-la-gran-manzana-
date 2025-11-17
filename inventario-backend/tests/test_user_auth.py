import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

# Set testing environment variable to use sync database driver BEFORE importing app
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient

from app.core.roles import Role
from app.core.security import create_access_token
from app.models.models import Usuario
from main import app

# --- Test Client ---
@pytest.fixture(scope="module")
def client():
    # Remove auth overrides to test real authentication
    from app.core.auth_middleware import get_current_active_user

    app.dependency_overrides.pop(get_current_active_user, None)
    return TestClient(app)


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


def test_register_user_success(client, _shared_db_session):
    unique_id = uuid.uuid4().hex[:8]
    username = f"newuser_{unique_id}"
    email = f"{username}@example.com"
    payload = {"username": username, "email": email, "password": "strongpassword", "rol_id": 1}
    
    # Clean up any existing user using the shared session
    existing_user = (
        _shared_db_session.query(Usuario)
        .filter((Usuario.nombre_usuario == username) | (Usuario.email == email))
        .first()
    )
    if existing_user:
        _shared_db_session.delete(existing_user)
        _shared_db_session.commit()

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
    # Verificar que tenga detail o estructura de error
    assert "detail" in data or ("success" in data and data["success"] is False)


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
