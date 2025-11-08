from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.auth_middleware import require_product_read, require_product_write
from app.crud.producto import (
    count_productos,
    create_producto,
    delete_producto,
    get_producto_by_id,
    get_productos,
    search_productos,
    update_producto,
)
from app.models.database import get_db
from app.models.schemas import (
    MessageResponse,
    ProductoBase,
    ProductoCreate,
    ProductoPaginatedResponse,
    ProductoResponse,
    ProductoUpdate,
)

router = APIRouter(tags=["Productos"])


def get_pagination_params(limit: int = Query(50, ge=1, le=1000), skip: int = Query(0, ge=0)):
    return {"limit": limit, "skip": skip}


# Search route must come BEFORE the {producto_id} route
@router.get("/search", response_model=dict)
async def buscar_productos(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_read()),
):
    """Buscar productos por texto"""
    try:
        productos = search_productos(db, q, skip, limit)
        productos_data = [ProductoBase.model_validate(p).model_dump() for p in productos]
        return {
            "success": True,
            "message": f"Encontrados {len(productos_data)} productos",
            "data": productos_data,
            "query": q,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}") from e


@router.get("/bajo-stock", response_model=dict)
async def productos_bajo_stock(
    db: Session = Depends(get_db), _: dict = Depends(require_product_read())
):
    """Obtener productos con stock bajo"""
    try:
        from app.crud.producto import get_productos_bajo_stock

        productos = get_productos_bajo_stock(db)
        productos_data = [ProductoBase.model_validate(p).model_dump() for p in productos]
        return {
            "success": True,
            "message": f"Encontrados {len(productos_data)} productos con stock bajo",
            "data": productos_data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener productos con stock bajo: {str(e)}"
        ) from e


@router.get("/por-vencer", response_model=dict)
async def productos_por_vencer(
    dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_read()),
):
    """Obtener productos próximos a vencer"""
    try:
        from app.crud.producto import get_productos_por_vencer

        productos = get_productos_por_vencer(db, dias)
        productos_data = [ProductoBase.model_validate(p).model_dump() for p in productos]
        return {
            "success": True,
            "message": f"Encontrados {len(productos_data)} productos próximos a vencer en {dias} días",
            "data": productos_data,
            "dias": dias,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener productos por vencer: {str(e)}"
        ) from e


@router.get("", response_model=ProductoPaginatedResponse)
async def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    nombre: str | None = None,
    id_seccion: int | None = None,
    id_laboratorio: int | None = None,
    estado: str | None = Query("Activo"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_read()),
):
    """Listar productos con filtros opcionales y paginación"""
    try:
        productos = get_productos(
            db=db,
            params={
                "skip": skip,
                "limit": limit,
                "nombre": nombre,
                "id_seccion": id_seccion,
                "id_laboratorio": id_laboratorio,
                "estado": estado,
            },
        )

        # Calcular total con COUNT() sobre los mismos filtros
        total = count_productos(
            db=db,
            nombre=nombre,
            id_seccion=id_seccion,
            id_laboratorio=id_laboratorio,
            estado=estado,
        )

        # Preparar filtros aplicados
        filters_applied = {}
        if nombre:
            filters_applied["nombre"] = nombre
        if id_seccion:
            filters_applied["id_seccion"] = id_seccion
        if id_laboratorio:
            filters_applied["id_laboratorio"] = id_laboratorio
        if estado:
            filters_applied["estado"] = estado

        # Convertir los objetos SQLAlchemy a diccionarios
        productos_dict = []
        for producto in productos:
            productos_dict.append(
                {
                    "id_producto": producto.id_producto,
                    "id_seccion": producto.id_seccion,
                    "id_laboratorio": producto.id_laboratorio,
                    "nombre_producto": producto.nombre_producto,
                    "principio_activo": producto.principio_activo,
                    "concentracion": producto.concentracion,
                    "forma_farmaceutica": producto.forma_farmaceutica,
                    "codigo_barras": producto.codigo_barras,
                    "requiere_receta": producto.requiere_receta,
                    "precio_compra": producto.precio_compra,
                    "stock_actual": producto.stock_actual,
                    "stock_minimo": producto.stock_minimo,
                    "descripcion": producto.descripcion,
                    "estado": producto.estado,
                }
            )

        return ProductoPaginatedResponse(
            success=True,
            message="Productos obtenidos exitosamente",
            data=productos_dict,
            pagination={
                "page": (skip // limit) + 1,
                "size": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
            filters_applied=filters_applied if filters_applied else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}") from e


@router.get("/{producto_id}", response_model=ProductoResponse)
async def obtener_producto(
    producto_id: int, db: Session = Depends(get_db), _: dict = Depends(require_product_read())
):
    """Obtener un producto específico por ID"""
    try:
        producto = get_producto_by_id(db, producto_id)
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Convertir el objeto SQLAlchemy a diccionario
        producto_dict = {
            "id_producto": producto.id_producto,
            "id_seccion": producto.id_seccion,
            "id_laboratorio": producto.id_laboratorio,
            "nombre_producto": producto.nombre_producto,
            "principio_activo": producto.principio_activo,
            "concentracion": producto.concentracion,
            "forma_farmaceutica": producto.forma_farmaceutica,
            "codigo_barras": producto.codigo_barras,
            "requiere_receta": producto.requiere_receta,
            "precio_compra": producto.precio_compra,
            "stock_actual": producto.stock_actual,
            "stock_minimo": producto.stock_minimo,
            "descripcion": producto.descripcion,
            "estado": producto.estado,
        }

        return {"success": True, "message": "Producto obtenido exitosamente", "data": producto_dict}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener producto: {str(e)}") from e


@router.post("", response_model=dict)
async def crear_producto(
    producto: ProductoCreate,
    response: Response,
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    """Crear un nuevo producto"""
    try:
        nuevo_producto = create_producto(db, producto)
        # Set Location header to created resource
        response.headers["Location"] = f"/api/v1/productos/{nuevo_producto.id_producto}"
        # Convertir el objeto SQLAlchemy a diccionario
        producto_dict = {
            "id_producto": nuevo_producto.id_producto,
            "id_seccion": nuevo_producto.id_seccion,
            "id_laboratorio": nuevo_producto.id_laboratorio,
            "nombre_producto": nuevo_producto.nombre_producto,
            "principio_activo": nuevo_producto.principio_activo,
            "concentracion": nuevo_producto.concentracion,
            "forma_farmaceutica": nuevo_producto.forma_farmaceutica,
            "codigo_barras": nuevo_producto.codigo_barras,
            "requiere_receta": nuevo_producto.requiere_receta,
            "precio_compra": nuevo_producto.precio_compra,
            "stock_actual": nuevo_producto.stock_actual,
            "stock_minimo": nuevo_producto.stock_minimo,
            "descripcion": nuevo_producto.descripcion,
            "estado": nuevo_producto.estado,
        }
        return {"success": True, "message": "Producto creado exitosamente", "data": producto_dict}
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}") from e


@router.put("/{producto_id}", response_model=ProductoResponse)
async def actualizar_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    """Actualizar un producto existente"""
    try:
        producto_actualizado = update_producto(db, producto_id, producto_update)
        if not producto_actualizado:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Convertir el objeto SQLAlchemy a diccionario
        producto_dict = {
            "id_producto": producto_actualizado.id_producto,
            "id_seccion": producto_actualizado.id_seccion,
            "id_laboratorio": producto_actualizado.id_laboratorio,
            "nombre_producto": producto_actualizado.nombre_producto,
            "principio_activo": producto_actualizado.principio_activo,
            "concentracion": producto_actualizado.concentracion,
            "forma_farmaceutica": producto_actualizado.forma_farmaceutica,
            "codigo_barras": producto_actualizado.codigo_barras,
            "requiere_receta": producto_actualizado.requiere_receta,
            "precio_compra": producto_actualizado.precio_compra,
            "stock_actual": producto_actualizado.stock_actual,
            "stock_minimo": producto_actualizado.stock_minimo,
            "descripcion": producto_actualizado.descripcion,
            "estado": producto_actualizado.estado,
        }

        return {
            "success": True,
            "message": "Producto actualizado exitosamente",
            "data": producto_dict,
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al actualizar producto: {str(e)}"
        ) from e


@router.delete("/{producto_id}", response_model=MessageResponse)
async def eliminar_producto(
    producto_id: int,
    modo: str = Query("logico", pattern="^(logico|fisico)$"),
    db: Session = Depends(get_db),
    _: dict = Depends(require_product_write()),
):
    """Eliminar un producto (lógico o físico)"""
    try:
        eliminado = delete_producto(db, producto_id, modo == "logico")
        if not eliminado:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        modo_texto = "lógicamente" if modo == "logico" else "físicamente"
        return {"success": True, "message": f"Producto eliminado {modo_texto} exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar producto: {str(e)}") from e
