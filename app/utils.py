from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

def crear_respuesta(
    success: bool = True,
    message: str = "",
    data: Optional[Any] = None,
    status_code: int = 200,
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    # Convert Pydantic models to dictionaries
    if isinstance(data, BaseModel):
        data = data.model_dump(mode='json')
    elif isinstance(data, list) and data and isinstance(data[0], BaseModel):
        data = [item.model_dump(mode='json') for item in data]

    contenido = {
        "success": success,
        "message": message,
        "data": data
    }
    if extra:
        contenido.update(extra)
    return JSONResponse(content=contenido, status_code=status_code)

def calcular_dias_para_vencer(fecha_vencimiento: Optional[datetime]) -> Optional[int]:
    if fecha_vencimiento is None:
        return None
    hoy = datetime.now().date()
    if isinstance(fecha_vencimiento, datetime):
        fecha = fecha_vencimiento.date()
    else:
        fecha = fecha_vencimiento
    delta = (fecha - hoy).days
    return delta if delta >= 0 else 0
