# app/routers/auth.py
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.audit_logging import audit_logger
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.crud.user import authenticate_user, create_user, get_user_by_email, get_user_by_username
from app.models.database import get_db
from app.models.models import Rol
from app.models.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    Token,
    UserCreate,
    UserResponse,
)

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
    request: Request = None,  # type: ignore[assignment]
):
    """
    Registrar un nuevo usuario
    """
    # Verificar si el nombre de usuario ya existe
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
        )

    # Verificar si el email ya existe
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Verificar que el rol exista
    role = db.query(Rol).filter(Rol.id_rol == user_data.rol_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role id")

    # Crear el usuario
    try:
        # Convertir RegisterRequest a UserCreate
        user_create = UserCreate(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            nombre_completo=user_data.nombre_completo,
            rol_id=user_data.rol_id,
        )
        user = create_user(db, user_create)

        # Log de auditoría
        if request:
            audit_logger.log_audit_event(
                event="user_registered",
                user_id=int(user.id_usuario),  # type: ignore[arg-type]
                ip_address=request.client.host if request.client else "unknown",
                details={"username": user.nombre_usuario, "email": user.email},
            )

        return UserResponse.model_validate(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists or invalid data"
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        ) from e


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None,  # type: ignore[assignment]
):
    """
    Autenticar usuario y obtener token de acceso
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Actualizar último acceso
    user.ultima_acceso = datetime.utcnow()  # type: ignore[assignment]
    db.commit()

    # Log de auditoría
    if request:
        audit_logger.log_audit_event(
            event="login",
            user_id=int(user.id_usuario),  # type: ignore[arg-type]
            ip_address=request.client.host if request.client else "unknown",
            details={"username": user.nombre_usuario},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.nombre_usuario}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-json", response_model=Token)
async def login_json(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticar usuario con JSON payload
    """
    user = authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password"
        )

    # Actualizar último acceso
    user.ultima_acceso = datetime.utcnow()  # type: ignore[assignment]
    db.commit()

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.nombre_usuario}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Obtener información del usuario actual
    """
    from app.core.security import verify_token

    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
        )

    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse.model_validate(user)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Cambiar contraseña del usuario actual
    """
    from app.core.security import verify_token

    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials"
        )

    user = get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verificar contraseña actual
    if not verify_password(password_data.current_password, str(user.password_hash)):  # type: ignore[arg-type]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )

    # Actualizar contraseña
    user.password_hash = get_password_hash(password_data.new_password)  # type: ignore[assignment]
    db.commit()

    return {"message": "Password changed successfully"}


@router.post("/reset-password-request")
async def request_password_reset(reset_data: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Solicitar restablecimiento de contraseña
    """
    user = get_user_by_email(db, reset_data.email)
    if user:
        # En un sistema real, aquí enviaríamos un email con el token
        # Por ahora, solo devolvemos un mensaje de éxito
        pass

    # Siempre devolver el mismo mensaje para evitar enumeración de emails
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password-confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Confirmar restablecimiento de contraseña
    """
    # En un sistema real, verificaríamos el token aquí
    # Por simplicidad, asumimos que el token es válido
    # y actualizamos la contraseña

    # Para este ejemplo, buscaremos por email en el token
    # En producción, usaríamos un sistema de tokens JWT o similar

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset functionality not fully implemented",
    )
