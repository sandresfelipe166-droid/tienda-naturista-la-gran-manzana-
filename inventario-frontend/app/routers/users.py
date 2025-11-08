# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.audit_logging import audit_logger
from app.core.auth_middleware import require_permission
from app.core.roles import Permission
from app.crud.user import delete_user, get_users, update_user
from app.models.database import get_db
from app.models.models import Usuario
from app.models.schemas import UserResponse, UserUpdate

router = APIRouter(tags=["Users"])


def get_pagination_params(limit: int = Query(50, ge=1, le=1000), skip: int = Query(0, ge=0)):
    return {"limit": limit, "skip": skip}


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.USER_READ)),
):
    """
    Listar usuarios (requiere permiso USER_READ)
    """
    limit = pagination.get("limit", 50)
    skip = pagination.get("skip", 0)
    users = get_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.USER_READ)),
):
    """
    Obtener usuario por ID (requiere permiso USER_READ)
    """
    user = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission(Permission.USER_WRITE)),
    request: Request = None,  # type: ignore[assignment]
):
    """
    Actualizar usuario (requiere permiso USER_WRITE)
    """
    try:
        updated_user = update_user(db, user_id, user_data.model_dump(exclude_unset=True))
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Log de auditoría
        if request:
            audit_logger.log_audit_event(
                event="user_updated",
                user_id=int(getattr(current_user, "id_usuario", 0)),
                ip_address=request.client.host if request.client else "unknown",
                details={
                    "updated_user_id": user_id,
                    "fields": list(user_data.model_dump(exclude_unset=True).keys()),
                },
            )

        return UserResponse.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/users/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permission(Permission.USER_DELETE)),
    request: Request = None,  # type: ignore[assignment]
):
    """
    Eliminar usuario lógicamente (requiere permiso USER_DELETE)
    """
    if int(getattr(current_user, "id_usuario", 0)) == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    success = delete_user(db, user_id, logical=True)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    # Log de auditoría
    if request:
        audit_logger.log_audit_event(
            event="user_deleted",
            user_id=int(getattr(current_user, "id_usuario", 0)),
            ip_address=request.client.host if request.client else "unknown",
            details={"deleted_user_id": user_id},
        )

    return {"message": "User deleted successfully"}
