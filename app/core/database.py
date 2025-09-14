from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# URL de conexión con tus datos exactos
SQLALCHEMY_DATABASE_URL = f"postgresql://admin:admin123@localhost:5432/inventario"

# Motor de base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # Para debug
    pool_pre_ping=True,
    pool_recycle=300
)

# Sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Función para obtener sesión de DB
def get_database():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()