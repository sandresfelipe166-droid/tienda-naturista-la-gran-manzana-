# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.database import get_db
from app.models.schemas import UserResponse, UserUpdate
from app.crud.user import get_users, get_user_by_username, update_user, delete_user
from app.core.auth_middleware import get_current_active_user
from app.core.audit_logging import audit_logger
from app.models.models import Usuario

router = APIRouter(tags=["Users"])

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Listar usuarios (solo administradores)
    """
    # TODO: Agregar verificación de permisos de admin
    users = get_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener usuario por ID
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
    current_user: Usuario = Depends(get_current_active_user),
    request: Request = None
):
    """
    Actualizar usuario
    """
    # TODO: Verificar permisos (solo admin o el propio usuario)
    try:
        updated_user = update_user(db, user_id, user_data.model_dump(exclude_unset=True))
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Log de auditoría
        if request:
            audit_logger.log_audit_event(
                event="user_updated",
                user_id=current_user.id_usuario,
                ip_address=request.client.host if request.client else "unknown",
                details={"updated_user_id": user_id, "fields": list(user_data.model_dump(exclude_unset=True).keys())}
            )

        return UserResponse.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user),
    request: Request = None
):
    """
    Eliminar usuario (lógico)
    """
    # TODO: Verificar permisos
    if current_user.id_usuario == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    success = delete_user(db, user_id, logical=True)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    # Log de auditoría
    if request:
        audit_logger.log_audit_event(
            event="user_deleted",
            user_id=current_user.id_usuario,
            ip_address=request.client.host if request.client else "unknown",
            details={"deleted_user_id": user_id}
        )

    return {"message": "User deleted successfully"}
