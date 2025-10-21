from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_product_read
from app.models.database import get_db
from app.models.schemas import InventorySummaryResponse
from app.services.producto_service import ProductoService

router = APIRouter(prefix="/inventory", tags=["Inventario"])


@router.get("", response_model=InventorySummaryResponse)
async def obtener_resumen_inventario(
    db: Session = Depends(get_db), _: dict = Depends(require_product_read())
):
    """Obtener resumen general del inventario"""
    try:
        # Obtener métricas del inventario
        total_productos = ProductoService.get_total_productos_activos(db)
        valor_total_stock = ProductoService.get_valor_total_stock(db)
        productos_bajo_stock = ProductoService.count_productos_bajo_stock(db)

        return {
            "success": True,
            "message": "Resumen de inventario obtenido exitosamente",
            "data": {
                "total_productos": total_productos,
                "valor_total_stock": round(valor_total_stock, 2),
                "productos_bajo_stock": productos_bajo_stock,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener resumen de inventario: {str(e)}"
        ) from e
