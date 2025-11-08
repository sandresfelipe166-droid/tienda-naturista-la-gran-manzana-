import os
import sys

import pytest

# Set TESTING environment variable for proper config
os.environ["TESTING"] = "true"
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.database import get_db
from app.models.models import Base
from main import app

# Setup file-based SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


import pytest

from app.models.models import Base, Laboratorio, Seccion


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Drop tables if exist, then create
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def seed_data():
    db = TestingSessionLocal()
    try:
        # Seed seccion
        seccion = Seccion(
            nombre_seccion="Seccion Test", descripcion="Descripcion test", estado="Activo"
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


# Mock user for authentication
class MockUser:
    def __init__(self):
        self.id_usuario = 1
        self.nombre_usuario = "testuser"
        self.email = "test@example.com"
        self.nombre_completo = "Test User"
        self.estado = "Activo"
        self.rol = MockRole()
        self.password_hash = "hashed"
        self.id_rol = 1
        self.fecha_creacion = None
        self.ultima_acceso = None


class MockRole:
    def __init__(self):
        self.id_rol = 1
        self.nombre_rol = "admin"


# Remove global dependency overrides for auth to allow proper 401/403 errors in tests
# Commenting out the overrides to test real auth behavior


def override_get_current_active_user():
    return MockUser()


def override_require_product_read():
    return MockUser()


def override_require_product_write():
    return MockUser()


# Import app after setting up override
from app.core.auth_middleware import (
    get_current_active_user,
    require_product_read,
    require_product_write,
)
from app.core.roles import Permission

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_active_user] = override_get_current_active_user
app.dependency_overrides[require_product_read] = override_require_product_read
app.dependency_overrides[require_product_write] = override_require_product_write


# Move TestClient inside a fixture to avoid import issues
@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_create_and_get_seccion(client):
    # Create seccion
    response = client.post(
        "/api/v1/secciones",
        json={
            "nombre_seccion": "Seccion Test",
            "descripcion": "Descripcion test",
            "ubicacion_fisica": None,
            "capacidad_maxima": 0,
            "temperatura_recomendada": None,
            "estado": "Activo",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    seccion_id = data["data"]["id_seccion"]

    # Get seccion
    response = client.get(f"/api/v1/secciones/{seccion_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["nombre_seccion"] == "Seccion Test"


def test_create_laboratorio_invalid_email(client):
    # Test creating laboratorio with invalid email
    response = client.post(
        "/api/v1/laboratorios",
        json={
            "nombre_laboratorio": "Laboratorio Test",
            "pais_origen": "Colombia",
            "telefono": "+573001234567",
            "email": "invalid-email",
            "direccion": "Calle 123",
            "estado": "Activo",
        },
    )
    assert response.status_code == 422  # Validation error


def test_update_seccion(client):
    # First create a seccion
    response = client.post(
        "/api/v1/secciones",
        json={
            "nombre_seccion": "Seccion Update Test",
            "descripcion": "Descripcion original",
            "ubicacion_fisica": None,
            "capacidad_maxima": 0,
            "temperatura_recomendada": None,
            "estado": "Activo",
        },
    )
    assert response.status_code == 200
    seccion_id = response.json()["data"]["id_seccion"]

    # Update the seccion (only required fields)
    response = client.put(
        f"/api/v1/secciones/{seccion_id}",
        json={
            "nombre_seccion": "Seccion Updated",
            "descripcion": "Descripcion actualizada",
            "estado": "Activo",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Sección actualizada exitosamente"


def test_create_laboratorio_success(client):
    response = client.post(
        "/api/v1/laboratorios",
        json={
            "nombre_laboratorio": "Laboratorio Success Test",
            "pais_origen": "Colombia",
            "telefono": "+573001234567",
            "email": "test@laboratorio.com",
            "direccion": "Calle 123",
            "estado": "Activo",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "id_laboratorio" in data["data"]


def test_create_seccion_duplicate_name(client):
    # Create first seccion
    response = client.post(
        "/api/v1/secciones",
        json={
            "nombre_seccion": "Seccion Duplicate",
            "descripcion": "Descripcion",
            "estado": "Activo",
        },
    )
    assert response.status_code == 200

    # Try to create another with same name
    response = client.post(
        "/api/v1/secciones",
        json={
            "nombre_seccion": "Seccion Duplicate",
            "descripcion": "Otra descripcion",
            "estado": "Activo",
        },
    )
    assert response.status_code == 500  # Unique constraint error handled as 500


def test_delete_producto(client):
    # First get an existing producto
    response = client.get("/api/v1/productos")
    if response.status_code == 200 and response.json()["data"]:
        producto_id = response.json()["data"][0]["id_producto"]

        # Delete producto (logical)
        response = client.delete(f"/api/v1/productos/{producto_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
