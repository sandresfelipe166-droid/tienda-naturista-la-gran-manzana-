import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.models import Usuario
from app.models.database import SessionLocal
from main import app

client = TestClient(app)


@pytest.fixture
def db():
    """Fixture para base de datos de pruebas"""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db: Session):
    """Crear un usuario de prueba"""
    user = Usuario(
        nombre_usuario="testuser",
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        nombre_completo="Test User",
        id_rol=1,
        estado="Activo",
        fecha_creacion=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestPasswordReset:
    """Tests para flujo de recuperación de contraseña"""

    def test_reset_password_request_user_exists(self, test_user: Usuario):
        """Probar solicitud de código cuando el usuario existe"""
        response = client.post(
            "/api/v1/auth/reset-password-request",
            json={"email": test_user.email},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # En modo debug o sin SMTP, debe devolver el código
        if "codigo" in data:
            assert len(data["codigo"]) == 6
            assert data["codigo"].isdigit()

    def test_reset_password_request_user_not_exists(self):
        """Probar solicitud de código para usuario inexistente"""
        response = client.post(
            "/api/v1/auth/reset-password-request",
            json={"email": "nonexistent@example.com"},
        )
        # Siempre devuelve 200 para evitar enumeración de emails
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_reset_password_confirm_success(self, db: Session, test_user: Usuario):
        """Probar confirmación exitosa de código"""
        # Generar un código
        codigo = "123456"
        test_user.codigo_recuperacion = codigo
        test_user.codigo_recuperacion_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

        # Confirmar el código
        response = client.post(
            "/api/v1/auth/reset-password-confirm",
            json={
                "email": test_user.email,
                "codigo": codigo,
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Password reset successfully"

        # Verificar que el código fue limpiado
        db.refresh(test_user)
        assert test_user.codigo_recuperacion == ""
        assert test_user.codigo_recuperacion_expiry is None

    def test_reset_password_confirm_invalid_code(self, db: Session, test_user: Usuario):
        """Probar confirmación con código inválido"""
        codigo = "123456"
        test_user.codigo_recuperacion = codigo
        test_user.codigo_recuperacion_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

        # Intentar con código incorrecto
        response = client.post(
            "/api/v1/auth/reset-password-confirm",
            json={
                "email": test_user.email,
                "codigo": "999999",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 400
        assert "Invalid recovery code" in response.json()["detail"]

    def test_reset_password_confirm_expired_code(self, db: Session, test_user: Usuario):
        """Probar confirmación con código expirado"""
        codigo = "123456"
        test_user.codigo_recuperacion = codigo
        # Código expirado hace 1 minuto
        test_user.codigo_recuperacion_expiry = datetime.utcnow() - timedelta(minutes=1)
        db.commit()

        response = client.post(
            "/api/v1/auth/reset-password-confirm",
            json={
                "email": test_user.email,
                "codigo": codigo,
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 400
        assert "expired" in response.json()["detail"].lower()

    def test_reset_password_lockout_after_failed_attempts(self, db: Session, test_user: Usuario):
        """Probar bloqueo después de múltiples intentos fallidos"""
        codigo = "123456"
        test_user.codigo_recuperacion = codigo
        test_user.codigo_recuperacion_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

        # Hacer 5 intentos fallidos
        for attempt in range(5):
            response = client.post(
                "/api/v1/auth/reset-password-confirm",
                json={
                    "email": test_user.email,
                    "codigo": "999999",
                    "new_password": "newpassword123",
                },
            )
            assert response.status_code == 400

        # Sexto intento debe devolver 429 (Too Many Requests)
        db.refresh(test_user)
        assert test_user.reset_attempts == 5
        assert test_user.reset_locked_until is not None

        response = client.post(
            "/api/v1/auth/reset-password-confirm",
            json={
                "email": test_user.email,
                "codigo": codigo,  # Incluso con código correcto
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 429
        assert "Too many failed attempts" in response.json()["detail"]

    def test_reset_password_lockout_expires(self, db: Session, test_user: Usuario):
        """Probar que el bloqueo expira después del tiempo"""
        # Simular bloqueo expirado hace 1 segundo
        test_user.reset_locked_until = datetime.utcnow() - timedelta(seconds=1)
        test_user.codigo_recuperacion = "123456"
        test_user.codigo_recuperacion_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

        # Debe permitir intento porque el bloqueo expiró
        response = client.post(
            "/api/v1/auth/reset-password-confirm",
            json={
                "email": test_user.email,
                "codigo": "123456",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 200

    def test_reset_password_clears_attempts_on_success(self, db: Session, test_user: Usuario):
        """Probar que los intentos fallidos se limpian al éxito"""
        test_user.reset_attempts = 3
        test_user.codigo_recuperacion = "123456"
        test_user.codigo_recuperacion_expiry = datetime.utcnow() + timedelta(minutes=15)
        db.commit()

        response = client.post(
            "/api/v1/auth/reset-password-confirm",
            json={
                "email": test_user.email,
                "codigo": "123456",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 200

        db.refresh(test_user)
        assert test_user.reset_attempts == 0
        assert test_user.reset_locked_until is None
