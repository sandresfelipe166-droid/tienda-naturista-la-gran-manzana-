# app/routers/roles.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_permission
from app.core.roles import Permission
from app.models.database import get_db
from app.models.models import Rol
from app.models.schemas import RolResponse

router = APIRouter(tags=["Roles"])


@router.get("/roles", response_model=list[RolResponse])
async def list_roles(
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.USER_READ)),
):
    """
    Listar todos los roles disponibles (requiere permiso USER_READ)
    """
    roles = db.query(Rol).all()
    return [RolResponse.model_validate(role) for role in roles]
