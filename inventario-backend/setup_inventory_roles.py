from app.models.database import SessionLocal
from app.models.models import Rol

db = SessionLocal()

# Actualizar roles para gestión de inventario
print("Configurando roles para GESTIÓN DE INVENTARIO...\n")

# Rol 1: Admin (ya existe)
admin = db.query(Rol).filter(Rol.id_rol == 1).first()
if admin:
    admin.nombre_rol = 'admin'
    admin.descripcion = 'Administrador con acceso total al sistema'
    print(f"✓ Rol 1: admin - Control total")

# Rol 2: Gestor de inventario (antes vendedor)
gestor = db.query(Rol).filter(Rol.id_rol == 2).first()
if gestor:
    gestor.nombre_rol = 'gestor'
    gestor.descripcion = 'Gestor de inventario - puede registrar entradas/salidas y editar productos'
    print(f"✓ Rol 2: gestor - Registra entradas/salidas, edita productos")

# Rol 3: Usuario regular -> cambiar a viewer si existe
user = db.query(Rol).filter(Rol.id_rol == 3).first()
if user:
    # Eliminar este rol si no se necesita
    db.delete(user)
    print(f"✗ Rol 3: user - ELIMINADO (no necesario)")

# Rol 4: Viewer (solo lectura)
viewer = db.query(Rol).filter(Rol.id_rol == 4).first()
if not viewer:
    viewer = Rol(
        id_rol=3,  # Cambiar a id 3
        nombre_rol='viewer',
        descripcion='Solo lectura - puede consultar inventario',
        permisos=None
    )
    db.add(viewer)
    print(f"✓ Rol 3: viewer - Solo consulta (creado)")
else:
    viewer.id_rol = 3  # Mover a id 3
    viewer.descripcion = 'Solo lectura - puede consultar inventario'
    print(f"✓ Rol 3: viewer - Solo consulta")

db.commit()

# Listar roles finales
print("\n" + "="*50)
print("ROLES FINALES PARA GESTIÓN DE INVENTARIO:")
print("="*50)
roles = db.query(Rol).order_by(Rol.id_rol).all()
for r in roles:
    print(f"  {r.id_rol}: {r.nombre_rol:12} - {r.descripcion}")

db.close()
