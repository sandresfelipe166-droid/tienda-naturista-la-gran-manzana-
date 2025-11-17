import os
import sys
from pathlib import Path

# Add project root to Python path so 'app' module can be imported
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure tests run in a test mode and use a local SQLite DB by default to avoid
# requiring a running PostgreSQL instance during unit tests on developers' machines.
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_db.sqlite")

# Import models so they are registered with Base.metadata (required for audit_trail)
from app.core.audit_trail import AuditLog  # noqa: E402, F401
from app.models.database import Base, get_db  # noqa: E402, F401
# Import ALL models BEFORE creating tables
from app.models import models  # noqa: E402, F401
from main import app  # noqa: E402
import app.models.database as db_module  # noqa: E402

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create all tables from Base.metadata AFTER importing all models
Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Force application engine during tests
db_module.engine = engine  # type: ignore[attr-defined]
db_module.SessionLocal = TestingSessionLocal  # type: ignore[attr-defined]


@pytest.fixture(autouse=True)
def _shared_db_session(monkeypatch: pytest.MonkeyPatch):
    """Create a single shared DB session per-test and use it everywhere (API + tests).

    This avoids visibility issues between different connections/transactions.
    """
    connection = engine.connect()
    transaction = connection.begin()
    # Recreate schema for this test on the shared connection
    Base.metadata.drop_all(bind=connection)
    Base.metadata.create_all(bind=connection)
    SessionForTest = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionForTest()

    # Seed minimal required data for tests (e.g., default role with id=1)
    try:
        # Ensure a role exists for foreign key constraints in Usuario
        if not session.query(models.Rol).filter_by(id_rol=1).first():
            session.add(models.Rol(id_rol=1, nombre_rol="Admin", descripcion="Default admin role"))
            session.commit()
    except Exception:
        session.rollback()
        raise

    # Patch SessionLocal() to return the same session instance
    monkeypatch.setattr(db_module, "SessionLocal", lambda: session, raising=False)

    # Override FastAPI dependency to yield the same session
    def _dep_override():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = _dep_override

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def db_session():
    """Provide a database session for tests."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# Override FastAPI dependency so API routes use the in-memory DB
def _override_get_db():
    """Backward compatibility, unused thanks to _shared_db_session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
