import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Set testing environment variable to use sync database driver BEFORE importing app
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///test.db"

import os

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.roles import Role
from app.core.security import create_access_token
from app.models.database import Base, SessionLocal, engine, get_db
from app.models.models import Laboratorio, Seccion
from main import app

# Create test engine and session
test_engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply override
app.dependency_overrides[get_db] = override_get_db


# Build a mock user with admin role (has PRODUCT_READ/WRITE)
class MockRole:
    def __init__(self, nombre_rol="admin"):
        self.id_rol = 1
        self.nombre_rol = nombre_rol


class MockUser:
    def __init__(self, nombre_usuario="testuser", rol="admin"):
        self.id_usuario = 1
        self.nombre_usuario = nombre_usuario
        self.email = "test@example.com"
        self.nombre_completo = "Test User"
        self.estado = "Activo"
        self.rol = MockRole(rol)
        self.password_hash = "hashed"
        self.id_rol = 1
        self.fecha_creacion = None
        self.ultima_acceso = None


def get_auth_headers(username: str, role: str) -> dict:
    """Generates a token and returns auth headers."""
    token = create_access_token(data={"sub": username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers() -> dict:
    return get_auth_headers("admin_user", Role.ADMIN.value)


@pytest.fixture
def viewer_headers() -> dict:
    return get_auth_headers("viewer_user", Role.VIEWER.value)


# --- Test Client ---
@pytest.fixture(scope="module")
def client():
    # Remove auth overrides to test real authentication
    from app.core.auth_middleware import (
        get_current_active_user,
        require_product_read,
        require_product_write,
    )

    app.dependency_overrides.pop(get_current_active_user, None)
    app.dependency_overrides.pop(require_product_read, None)
    app.dependency_overrides.pop(require_product_write, None)
    return TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Drop tables if exist, then create
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="module")
def seed_data():
    db = TestingSessionLocal()
    try:
        # Seed seccion
        seccion = Seccion(
            nombre_seccion="Seccion Test", descripcion="Seccion para pruebas", estado="Activo"
        )
        db.add(seccion)
        db.flush()
        seccion_id = seccion.id_seccion

        # Seed laboratorio
        laboratorio = Laboratorio(nombre_laboratorio="Laboratorio Test", estado="Activo")
        db.add(laboratorio)
        db.flush()
        laboratorio_id = laboratorio.id_laboratorio

        db.commit()
        yield {"seccion_id": seccion_id, "laboratorio_id": laboratorio_id}
    finally:
        db.close()


# --- Tests ---
def test_list_productos_unauthenticated(client):
    response = client.get("/api/v1/productos/")
    assert response.status_code == 401  # Unauthorized
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "Not authenticated"


def test_list_productos_authenticated_as_admin(client, admin_headers):
    with (
        patch("app.core.auth_middleware.get_current_user_from_token") as mock_get_user,
        patch("app.crud.producto.get_productos") as mock_get_productos,
    ):
        mock_get_user.return_value = MockUser()
        mock_get_productos.return_value = []
        response = client.get("/api/v1/productos/", headers=admin_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "data" in body


def test_create_producto_unauthenticated(client):
    response = client.post("/api/v1/productos/", json={})
    assert response.status_code == 401  # Unauthorized
    data = response.json()
    assert data["success"] is False
    assert data["error"]["message"] == "Not authenticated"


def test_create_producto_as_viewer_is_forbidden(client, viewer_headers):
    with patch("app.core.auth_middleware.get_current_user_from_token") as mock_get_user:
        mock_get_user.return_value = MockUser("viewer_user", "viewer")
        payload = {
            "id_seccion": 1,
            "id_laboratorio": 1,
            "nombre_producto": "Test Producto",
            "principio_activo": "Test",
            "concentracion": "10mg",
            "forma_farmaceutica": "Tableta",
            "codigo_barras": "123456789",
            "requiere_receta": False,
            "precio_compra": 10.0,
            "stock_actual": 100,
            "stock_minimo": 10,
            "descripcion": "Test producto",
            "estado": "Activo",
        }
        response = client.post("/api/v1/productos/", json=payload, headers=viewer_headers)
        assert response.status_code == 403  # Forbidden
        data = response.json()
        assert data["success"] is False
        assert "Permission" in data["error"]["message"]


def test_create_producto_as_admin_success(client, admin_headers, seed_data):
    seccion_id = seed_data["seccion_id"]
    laboratorio_id = seed_data["laboratorio_id"]

    with patch("app.core.auth_middleware.get_current_user_from_token") as mock_get_user:
        mock_get_user.return_value = MockUser()

        payload = {
            "id_seccion": seccion_id,
            "id_laboratorio": laboratorio_id,
            "nombre_producto": "Test Producto Creado",
            "precio_compra": 10.0,
            "stock_actual": 0,
            "stock_minimo": 0,
            "estado": "Activo",
        }
        response = client.post("/api/v1/productos/", json=payload, headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["nombre_producto"] == "Test Producto Creado"
