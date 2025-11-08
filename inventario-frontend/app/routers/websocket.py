"""
Router WebSocket para notificaciones en tiempo real.

Endpoints:
- /api/v1/ws/notifications - WebSocket para notificaciones generales
- /api/v1/ws/alerts - WebSocket para alertas de inventario
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.core.websocket_manager import handle_websocket_connection, ws_manager
from app.models.database import get_db
from app.models.models import Usuario

router = APIRouter()


@router.websocket("/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """
    WebSocket para notificaciones generales en tiempo real.
    
    Autenticación opcional: enviar token JWT como primer mensaje:
    {"type": "auth", "token": "your_jwt_token"}
    """
    user_id = None
    username = None
    roles = []
    
    # Aceptar conexión temporalmente
    await websocket.accept()
    
    try:
        # Esperar mensaje de autenticación (timeout 10s)
        import asyncio
        try:
            auth_message = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=10.0
            )
            
            if auth_message.get("type") == "auth":
                token = auth_message.get("token")
                if token:
                    try:
                        # Verificar token
                        from app.core.security import verify_token
                        username = verify_token(token)
                        
                        if username:
                            # Obtener usuario de la base de datos
                            from app.crud.user import get_user_by_username
                            usuario = get_user_by_username(db, username)
                            if usuario:
                                user_id = usuario.usuario_id
                                roles = [usuario.rol.nombre_rol] if usuario.rol else []
                    except Exception:
                        pass  # Continuar como anónimo
        
        except asyncio.TimeoutError:
            pass  # Continuar como anónimo
        
        # Desconectar temporalmente y reconectar con manager
        await ws_manager.disconnect(websocket)
        await handle_websocket_connection(
            websocket,
            user_id=user_id,
            username=username,
            roles=roles,
            enable_heartbeat=True
        )
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)


@router.websocket("/alerts")
async def websocket_alerts_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """
    WebSocket específico para alertas de inventario.
    
    Envía notificaciones de:
    - Stock bajo
    - Productos próximos a expirar
    - Productos expirados
    - Alertas críticas
    """
    await handle_websocket_connection(
        websocket,
        user_id=None,
        username="alerts_client",
        roles=[],
        enable_heartbeat=True
    )


@router.get("/connections")
async def get_websocket_connections():
    """
    Obtener información de conexiones WebSocket activas.
    
    Requiere autenticación de admin.
    """
    return {
        "total_connections": ws_manager.get_connections_count(),
        "connections": ws_manager.get_connections_info(),
    }
