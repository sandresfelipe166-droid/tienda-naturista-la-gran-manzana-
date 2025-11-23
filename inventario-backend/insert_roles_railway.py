"""
Script simple para insertar roles en la base de datos de Railway
Ejecutar con: python insert_roles_railway.py
"""
import os
import sys

# Configurar la DATABASE_URL de Railway
os.environ['DATABASE_URL'] = "postgresql://postgres:fPLKsUJkqCXDvVhtKwfWBxIcBdaRfYop@tramway.proxy.rlwy.net:53931/railway"

# Añadir el directorio al path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Rol

# Roles por defecto
DEFAULT_ROLES = [
    {
        "nombre_rol": "Admin",
        "descripcion": "Administrador del sistema con acceso completo",
        "permisos": "all"
    },
    {
        "nombre_rol": "Gerente", 
        "descripcion": "Gerente con permisos de gestión",
        "permisos": "read,write,update,delete"
    },
    {
        "nombre_rol": "Empleado",
        "descripcion": "Empleado con permisos básicos", 
        "permisos": "read,write"
    }
]

def insert_roles():
    """Insertar roles en la base de datos"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL no está configurada")
        print("Configúrala con: $env:DATABASE_URL='postgresql://...'")
        return False
        
    print(f"Conectando a Railway PostgreSQL...")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Verificar roles existentes
        existing = {r.nombre_rol for r in session.query(Rol).all()}
        print(f"Roles existentes: {existing if existing else 'ninguno'}")
        
        # Insertar roles faltantes
        inserted = []
        for role_data in DEFAULT_ROLES:
            nombre = role_data['nombre_rol']
            if nombre not in existing:
                rol = Rol(
                    nombre_rol=nombre,
                    descripcion=role_data['descripcion'],
                    permisos=role_data['permisos']
                )
                session.add(rol)
                inserted.append(nombre)
        
        if inserted:
            session.commit()
            print(f"✅ Roles insertados: {', '.join(inserted)}")
        else:
            print("✓ Todos los roles ya existen")
            
        # Verificar
        all_roles = session.query(Rol).all()
        print(f"\n📋 Roles en la base de datos:")
        for rol in all_roles:
            print(f"  - {rol.nombre_rol}: {rol.descripcion}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("INSERTAR ROLES EN RAILWAY")
    print("=" * 60)
    success = insert_roles()
    sys.exit(0 if success else 1)
