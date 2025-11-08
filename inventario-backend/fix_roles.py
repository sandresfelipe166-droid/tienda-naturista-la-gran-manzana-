from app.models.database import SessionLocal
from app.models.models import Rol

db = SessionLocal()

print("="*60)
print("CONFIGURANDO ROLES PARA GESTIÓN DE INVENTARIO")
print("="*60 + "\n")

# Eliminar todos los roles existentes excepto los que queremos
db.query(Rol).filter(Rol.id_rol.notin_([1, 2, 3])).delete(synchronize_session=False)

# Configurar los 3 roles necesarios
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
        # Actualizar
        rol.nombre_rol = config['nombre_rol']
        rol.descripcion = config['descripcion']
        print(f"✓ Actualizado: {config['id_rol']} - {config['nombre_rol']}")
    else:
        # Crear
        nuevo_rol = Rol(**config, permisos=None)
        db.add(nuevo_rol)
        print(f"✓ Creado: {config['id_rol']} - {config['nombre_rol']}")

db.commit()

# Mostrar resultado final
print("\n" + "="*60)
print("ROLES CONFIGURADOS:")
print("="*60)
roles = db.query(Rol).order_by(Rol.id_rol).all()
for r in roles:
    emoji = "👑" if r.nombre_rol == "admin" else "📦" if r.nombre_rol == "gestor" else "👁️"
    print(f"  {emoji} {r.id_rol}: {r.nombre_rol:10} - {r.descripcion}")

print("\n" + "="*60)
db.close()
