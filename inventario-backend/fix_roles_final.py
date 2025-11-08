from app.models.database import SessionLocal
from app.models.models import Rol, Usuario

db = SessionLocal()

print("="*60)
print("LIMPIEZA Y CONFIGURACIÓN DE ROLES")
print("="*60 + "\n")

# 1. Actualizar usuarios con rol 4 (viewer antiguo) a rol 3
usuarios_rol4 = db.query(Usuario).filter(Usuario.id_rol == 4).all()
if usuarios_rol4:
    print(f"Actualizando {len(usuarios_rol4)} usuarios de rol 4 a rol 3...")
    for user in usuarios_rol4:
        user.id_rol = 3
    db.commit()
    print("✓ Usuarios actualizados\n")

# 2. Eliminar rol 4 si existe
rol4 = db.query(Rol).filter(Rol.id_rol == 4).first()
if rol4:
    db.delete(rol4)
    db.commit()
    print("✓ Rol 4 eliminado\n")

# 3. Configurar los 3 roles necesarios
roles_config = [
    {
        'id_rol': 1,
        'nombre_rol': 'admin',
        'descripcion': 'Administrador con acceso total al sistema'
    },
    {
        'id_rol': 2,
        'nombre_rol': 'gestor',
        'descripcion': 'Gestor de inventario - registra entradas/salidas y edita productos'
    },
    {
        'id_rol': 3,
        'nombre_rol': 'viewer',
        'descripcion': 'Solo lectura - puede consultar inventario'
    }
]

for config in roles_config:
    rol = db.query(Rol).filter(Rol.id_rol == config['id_rol']).first()
    if rol:
        rol.nombre_rol = config['nombre_rol']
        rol.descripcion = config['descripcion']
        print(f"✓ Actualizado: {config['id_rol']} - {config['nombre_rol']}")
    else:
        nuevo_rol = Rol(**config, permisos=None)
        db.add(nuevo_rol)
        print(f"✓ Creado: {config['id_rol']} - {config['nombre_rol']}")

db.commit()

# 4. Mostrar resultado final
print("\n" + "="*60)
print("ROLES PARA GESTIÓN DE INVENTARIO:")
print("="*60)
roles = db.query(Rol).order_by(Rol.id_rol).all()
for r in roles:
    emoji = "👑" if r.nombre_rol == "admin" else "📦" if r.nombre_rol == "gestor" else "👁️"
    count = db.query(Usuario).filter(Usuario.id_rol == r.id_rol).count()
    print(f"  {emoji} {r.id_rol}: {r.nombre_rol:10} - {r.descripcion} ({count} usuarios)")

print("\n" + "="*60)
db.close()
