"""
Script para crear las tablas de la base de datos manualmente
Ejecutar localmente apuntando a la BD de Railway
"""
import os
import sys

# Añadir el directorio actual al path para importar app
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from app.models.database import Base
from app.models import models  # Importar todos los modelos
from app.core.config import settings

def create_all_tables():
    """Crear todas las tablas usando SQLAlchemy"""
    print(f"Conectando a: {settings.database_url.split('@')[1]}")
    
    engine = create_engine(settings.database_url)
    
    # Primero limpiamos el schema public si existe
    with engine.connect() as conn:
        print("Limpiando schema public...")
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
        print("✓ Schema limpio creado")
    
    # Crear todas las tablas
    print("\nCreando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente")
    
    # Verificar tablas creadas
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"\n✓ Tablas en la base de datos: {', '.join(tables)}")
    
    # Crear roles iniciales
    print("\nCreando roles iniciales...")
    from app.scripts.seed_roles import seed_roles
    roles_created = seed_roles()
    if roles_created:
        print(f"✓ Roles creados: {', '.join(roles_created)}")
    else:
        print("✓ Roles ya existen")

if __name__ == "__main__":
    create_all_tables()
    print("\n✅ Base de datos inicializada correctamente")
