from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.roles import Permission, Role, get_role_permissions, has_permission
from app.core.security import verify_token
from app.crud.user import get_user_by_username
from app.models.database import get_db

# Use the same OAuth2 scheme across the app for consistent Swagger auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user_from_token(token: str, db: Session):
    """Obtener usuario actual desde token"""
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
        )

    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def get_current_active_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)  # noqa: B008
):
    """Dependency para obtener usuario activo actual"""
    return get_current_user_from_token(token, db)


def require_role(required_role: str):
    """Decorator para requerir un rol específico"""

    def role_checker(
        user=Depends(get_current_active_user),  # noqa: B008
    ):
        # Compare role name as string to support both enums and DB-stored strings
        current_role = getattr(getattr(user, "rol", None), "nombre_rol", None)
        required_role_value = required_role.value if hasattr(required_role, "value") else required_role  # type: ignore[attr-defined]
        if current_role != required_role_value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{required_role}' required"
            )
        return user

    return role_checker


def require_admin(
    user=Depends(get_current_active_user),  # noqa: B008
):
    """Dependency para requerir rol de administrador"""
    current_role = getattr(getattr(user, "rol", None), "nombre_rol", None)
    if current_role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{Role.ADMIN.value}' required"
        )
    return user


def require_manager(
    user=Depends(get_current_active_user),  # noqa: B008
):
    """Dependency para requerir rol de manager"""
    current_role = getattr(getattr(user, "rol", None), "nombre_rol", None)
    if current_role != Role.MANAGER.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Role '{Role.MANAGER.value}' required"
        )
    return user


def get_user_permissions(user) -> list[str]:
    """Obtener permisos del usuario basado en su rol"""
    if user.rol and user.rol.nombre_rol:
        return get_role_permissions(user.rol.nombre_rol)
    return []


def require_permission(required_permission: str):
    """Decorator para requerir un permiso específico"""

    def permission_checker(
        user=Depends(get_current_active_user),  # noqa: B008
    ):
        user_permissions = get_user_permissions(user)
        if not has_permission(user_permissions, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{required_permission}' required",
            )
        return user

    return permission_checker


def require_any_permission(required_permissions: list[str]):
    """Decorator para requerir cualquiera de los permisos especificados"""

    def permission_checker(
        user=Depends(get_current_active_user),  # noqa: B008
    ):
        user_permissions = get_user_permissions(user)
        if not any(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of the following permissions required: {', '.join(required_permissions)}",
            )
        return user

    return permission_checker


def require_all_permissions(required_permissions: list[str]):
    """Decorator para requerir todos los permisos especificados"""

    def permission_checker(
        user=Depends(get_current_active_user),  # noqa: B008
    ):
        user_permissions = get_user_permissions(user)
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All of the following permissions required: {', '.join(required_permissions)}",
            )
        return user

    return permission_checker


# Convenience functions for common permission checks
def require_product_read():
    return require_permission(Permission.PRODUCT_READ)


def require_product_write():
    return require_permission(Permission.PRODUCT_WRITE)


def require_user_management():
    return require_permission(Permission.USER_READ)
