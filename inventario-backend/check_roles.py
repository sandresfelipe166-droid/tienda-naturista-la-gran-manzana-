from app.models.database import SessionLocal
from app.models.models import Rol

db = SessionLocal()
roles = db.query(Rol).all()
print(f'Roles encontrados: {len(roles)}')
for r in roles:
    print(f'  - {r.id_rol}: {r.nombre_rol}')
db.close()
