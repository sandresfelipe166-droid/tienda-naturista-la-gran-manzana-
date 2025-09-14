from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
from typing import Generator
import os
from app.core.config import settings

# Normalize async driver to sync driver always; tests further normalize plain postgresql to psycopg2
database_url = settings.database_url
if database_url.startswith("postgresql+asyncpg://"):
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)

# Force sync driver for testing (also convert plain postgresql to psycopg2)
if os.getenv("TESTING") == "true":
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=getattr(settings, "debug", False)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception:
        # Ensure the session is rolled back on errors to avoid invalid state
        db.rollback()
        raise
    finally:
        db.close()
