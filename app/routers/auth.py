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
    import random
    import string
    import smtplib
    from email.message import EmailMessage

    codigo = None  # Inicializar fuera del bloque if
    user = get_user_by_email(db, reset_data.email)
    if user:
        # Generar código de recuperación de 6 dígitos
        codigo = ''.join(random.choices(string.digits, k=6))
        user.codigo_recuperacion = codigo  # type: ignore[assignment]
        # Expira en X minutos (configurable)
        expiry = datetime.utcnow() + timedelta(minutes=getattr(settings, "password_reset_expire_minutes", 15))
        user.codigo_recuperacion_expiry = expiry  # type: ignore[assignment]
        # Limpiar intentos fallidos previos
        user.reset_attempts = 0  # type: ignore[assignment]
        user.reset_locked_until = None  # type: ignore[assignment]
        db.commit()
        
        # Si SMTP está configurado, envia el correo; si no, en modo debug devolvemos el código para pruebas
        try:
            if settings.smtp_host and settings.smtp_user and settings.smtp_password:
                msg = EmailMessage()
                msg['Subject'] = 'Recuperación de contraseña - Código'
                msg['From'] = settings.smtp_user
                msg['To'] = reset_data.email
                msg.set_content(f"Su código de recuperación es: {codigo}\nCaduca a las {expiry.isoformat()} UTC")
                with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                    if settings.smtp_use_tls:
                        smtp.starttls()
                    smtp.login(settings.smtp_user, settings.smtp_password)
                    smtp.send_message(msg)
                # No devolvemos el código en la respuesta en producción
                return {"message": "If the email exists, a password reset code has been sent"}
        except Exception as e:
            # Log the failure but don't raise so recovery still works in dev
            try:
                from app.core import audit_logging

                audit_logging.audit_logger.log_audit_event(
                    event="password_reset_email_failed",
                    user_id=user.id_usuario if user.id_usuario is not None else 0,  # type: ignore[arg-type]
                    ip_address="unknown",
                    details={"error": str(e)},
                )
            except Exception:
                pass
            # If SMTP sending fails, fallback to returning code in debug

        # En desarrollo o si SMTP no está configurado devolvemos el código para facilitar pruebas
        if settings.debug and codigo:
            return {"message": "Código de recuperación generado", "codigo": codigo}
    
    # Siempre devolver el mismo mensaje para evitar enumeración de emails
    return {"message": "If the email exists, a password reset code has been sent"}


@router.post("/reset-password-confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Confirmar restablecimiento de contraseña
    """
    # Validar que las contraseñas cumplan con requisitos mínimos
    if len(reset_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    user = get_user_by_email(db, reset_data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Verificar si el usuario está bloqueado por intentos fallidos
    reset_locked_until = getattr(user, "reset_locked_until", None)
    if reset_locked_until and datetime.utcnow() < reset_locked_until:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Try again later."
        )
    
    # Acceder al valor real del campo y su expiración
    codigo_actual = getattr(user, "codigo_recuperacion", None)
    codigo_expiry = getattr(user, "codigo_recuperacion_expiry", None)
    
    # Validar código
    if not codigo_actual or codigo_actual != reset_data.codigo:
        # Incrementar contador de intentos fallidos
        reset_attempts = getattr(user, "reset_attempts", 0) or 0
        reset_attempts += 1
        setattr(user, "reset_attempts", reset_attempts)
        
        # Bloquear después de 5 intentos fallidos por 15 minutos
        if reset_attempts >= 5:
            locked_until = datetime.utcnow() + timedelta(minutes=15)
            setattr(user, "reset_locked_until", locked_until)
        
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid recovery code")
    
    # Validar expiración del código
    if not codigo_expiry or datetime.utcnow() > codigo_expiry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recovery code expired")
    
    # Éxito: actualizar contraseña y limpiar
    setattr(user, "password_hash", get_password_hash(reset_data.new_password))
    setattr(user, "codigo_recuperacion", None)
    setattr(user, "codigo_recuperacion_expiry", None)
    setattr(user, "reset_attempts", 0)
    setattr(user, "reset_locked_until", None)
    db.commit()
    
    # Log de auditoría
    try:
        from app.core import audit_logging
        audit_logging.audit_logger.log_audit_event(
            event="password_reset_confirmed",
            user_id=user.id_usuario if user.id_usuario is not None else 0,  # type: ignore[arg-type]
            ip_address="unknown",
            details={"email": reset_data.email},
        )
    except Exception:
        pass
    
    return {"message": "Password reset successfully"}
