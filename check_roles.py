import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))
from app.models.database import SessionLocal
from app.models.models import Rol
db = SessionLocal()
roles = db.query(Rol).all()
for r in roles:
    print(f'id: {r.id_rol}, name: {r.nombre_rol}')
db.close()
