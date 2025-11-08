from app.models.database import SessionLocal
from app.models.models import Rol

db = SessionLocal()

# Verificar si existe vendedor
vendedor = db.query(Rol).filter(Rol.nombre_rol == 'vendedor').first()
if not vendedor:
    print("Creando rol 'vendedor'...")
    # Actualizar el rol 'manager' a 'vendedor' o crear uno nuevo
    manager = db.query(Rol).filter(Rol.nombre_rol == 'manager').first()
    if manager:
        manager.nombre_rol = 'vendedor'
        manager.descripcion = 'Vendedor con acceso a ventas y entradas'
        db.commit()
        print(f"✓ Rol 'manager' actualizado a 'vendedor' (id: {manager.id_rol})")
    else:
        # Crear nuevo rol vendedor con id=2
        nuevo_vendedor = Rol(
            id_rol=2,
            nombre_rol='vendedor',
            descripcion='Vendedor con acceso a ventas y entradas',
            permisos=None
        )
        db.add(nuevo_vendedor)
        db.commit()
        print(f"✓ Rol 'vendedor' creado con id: 2")
else:
    print(f"✓ Rol 'vendedor' ya existe (id: {vendedor.id_rol})")

# Listar roles finales
print("\nRoles actuales:")
roles = db.query(Rol).order_by(Rol.id_rol).all()
for r in roles:
    print(f"  {r.id_rol}: {r.nombre_rol}")

db.close()
