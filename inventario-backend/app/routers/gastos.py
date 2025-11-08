"""Router para gestión de gastos."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_permission
from app.core.roles import Permission
from app.models import models, schemas
from app.models.database import get_db

router = APIRouter(prefix="/gastos", tags=["Gastos"])


@router.post("/", response_model=schemas.GastoResponse, status_code=status.HTTP_201_CREATED)
def crear_gasto(
    gasto: schemas.GastoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    """Crear un nuevo gasto."""
    db_gasto = models.Gasto(id_usuario=current_user.id_usuario, **gasto.model_dump())
    db.add(db_gasto)
    db.commit()
    db.refresh(db_gasto)
    return db_gasto


@router.get("/", response_model=list[schemas.GastoResponse])
def listar_gastos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    mes: int | None = Query(None, ge=1, le=12),
    año: int | None = Query(None, ge=2000),
    categoria: str | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Listar gastos con filtros opcionales."""
    query = db.query(models.Gasto)

    if mes:
        query = query.filter(extract('month', models.Gasto.fecha_gasto) == mes)
    if año:
        query = query.filter(extract('year', models.Gasto.fecha_gasto) == año)
    if categoria:
        query = query.filter(models.Gasto.categoria == categoria)

    gastos = query.order_by(models.Gasto.fecha_gasto.desc()).offset(skip).limit(limit).all()
    return gastos


@router.get("/{id_gasto}", response_model=schemas.GastoResponse)
def obtener_gasto(
    id_gasto: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Obtener detalles de un gasto específico."""
    gasto = db.query(models.Gasto).filter(models.Gasto.id_gasto == id_gasto).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return gasto


@router.get("/estadisticas/mes", response_model=schemas.GastoEstadisticasMes)
def estadisticas_gastos_mes(
    mes: int = Query(..., ge=1, le=12),
    año: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Obtener estadísticas de gastos de un mes específico."""
    # Total del mes
    resultado_total = (
        db.query(
            func.sum(models.Gasto.monto).label("total_gastos"),
            func.count(models.Gasto.id_gasto).label("cantidad_gastos"),
        )
        .filter(
            extract('month', models.Gasto.fecha_gasto) == mes,
            extract('year', models.Gasto.fecha_gasto) == año,
            models.Gasto.estado == "Activo",
        )
        .first()
    )

    # Total por categoría
    resultado_categorias = (
        db.query(models.Gasto.categoria, func.sum(models.Gasto.monto).label("total"))
        .filter(
            extract('month', models.Gasto.fecha_gasto) == mes,
            extract('year', models.Gasto.fecha_gasto) == año,
            models.Gasto.estado == "Activo",
        )
        .group_by(models.Gasto.categoria)
        .all()
    )

    por_categoria = {r.categoria: r.total for r in resultado_categorias}

    return {
        "mes": mes,
        "año": año,
        "total_gastos": getattr(resultado_total, "total_gastos", 0.0) or 0.0,
        "cantidad_gastos": getattr(resultado_total, "cantidad_gastos", 0) or 0,
        "por_categoria": por_categoria,
    }


@router.get("/estadisticas/año", response_model=schemas.GastoEstadisticasAño)
def estadisticas_gastos_año(
    año: int = Query(..., ge=2000),
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_READ)),
):
    """Obtener estadísticas de gastos de un año completo."""
    # Total del año
    resultado_año = (
        db.query(
            func.sum(models.Gasto.monto).label("total_gastos"),
            func.count(models.Gasto.id_gasto).label("cantidad_gastos"),
        )
        .filter(extract('year', models.Gasto.fecha_gasto) == año, models.Gasto.estado == "Activo")
        .first()
    )

    # Estadísticas por mes
    resultado_meses = (
        db.query(
            extract('month', models.Gasto.fecha_gasto).label("mes"),
            func.sum(models.Gasto.monto).label("total_gastos"),
            func.count(models.Gasto.id_gasto).label("cantidad_gastos"),
        )
        .filter(extract('year', models.Gasto.fecha_gasto) == año, models.Gasto.estado == "Activo")
        .group_by(extract('month', models.Gasto.fecha_gasto))
        .all()
    )

    meses = []
    for r in resultado_meses:
        # Obtener gastos por categoría para este mes
        resultado_cat = (
            db.query(models.Gasto.categoria, func.sum(models.Gasto.monto).label("total"))
            .filter(
                extract('month', models.Gasto.fecha_gasto) == int(r.mes),
                extract('year', models.Gasto.fecha_gasto) == año,
                models.Gasto.estado == "Activo",
            )
            .group_by(models.Gasto.categoria)
            .all()
        )

        por_categoria = {cat.categoria: cat.total for cat in resultado_cat}

        meses.append(
            {
                "mes": int(r.mes),
                "año": año,
                "total_gastos": r.total_gastos or 0.0,
                "cantidad_gastos": r.cantidad_gastos or 0,
                "por_categoria": por_categoria,
            }
        )

    return {
        "año": año,
        "total_gastos": getattr(resultado_año, "total_gastos", 0.0) or 0.0,
        "cantidad_gastos": getattr(resultado_año, "cantidad_gastos", 0) or 0,
        "meses": meses,
    }


@router.patch("/{id_gasto}", response_model=schemas.GastoResponse)
def actualizar_gasto(
    id_gasto: int,
    gasto_update: schemas.GastoUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_WRITE)),
):
    """Actualizar un gasto."""
    gasto = db.query(models.Gasto).filter(models.Gasto.id_gasto == id_gasto).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    update_data = gasto_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gasto, field, value)

    db.commit()
    db.refresh(gasto)
    return gasto


@router.delete("/{id_gasto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_gasto(
    id_gasto: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_permission(Permission.INVENTORY_DELETE)),
):
    """Eliminar (marcar como inactivo) un gasto."""
    gasto = db.query(models.Gasto).filter(models.Gasto.id_gasto == id_gasto).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")

    gasto.estado = "Inactivo"  # type: ignore[assignment]
    db.commit()
    return None
