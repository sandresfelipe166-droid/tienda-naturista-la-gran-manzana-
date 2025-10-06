"""
Router avanzado de productos con filtros, paginación y caché
"""
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.database import get_db
from app.models.schemas import ProductoResponse, MessageResponse
from app.models.filters import ProductoFilters
from app.models.pagination import PaginationParams
from app.crud.producto_advanced import (
    get_productos_advanced,
    search_productos_advanced,
    get_productos_stats,
    get_top_productos,
    get_productos_por_laboratorio_stats,
    get_productos_por_seccion_stats
)
from app.core.cache import cache_manager
from app.core.auth_middleware import get_current_active_user
from app.models.models import Usuario

router = APIRouter(prefix="/productos", tags=["productos-advanced"])


@router.get("/advanced", response_model=dict)
async def get_productos_with_filters(
    # Filtros de búsqueda
    nombre: Optional[str] = Query(None, description="Buscar por nombre"),
    codigo_barras: Optional[str] = Query(None, description="Buscar por código de barras"),
    principio_activo: Optional[str] = Query(None, description="Buscar por principio activo"),
    id_laboratorio: Optional[int] = Query(None, description="Filtrar por laboratorio"),
    id_seccion: Optional[int] = Query(None, description="Filtrar por sección"),
    precio_min: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    precio_max: Optional[float] = Query(None, ge=0, description="Precio máximo"),
    stock_min: Optional[int] = Query(None, ge=0, description="Stock mínimo"),
    stock_max: Optional[int] = Query(None, ge=0, description="Stock máximo"),
    stock_bajo: Optional[bool] = Query(None, description="Solo productos con stock bajo"),
    requiere_receta: Optional[bool] = Query(None, description="Filtrar por receta requerida"),
    estado: Optional[str] = Query("Activo", description="Estado del producto"),
    forma_farmaceutica: Optional[str] = Query(None, description="Forma farmacéutica"),
    # Paginación
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(50, ge=1, le=100, description="Elementos por página"),
    # Ordenamiento
    sort_by: str = Query("nombre_producto", description="Campo para ordenar"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Dirección del ordenamiento"),
    # Dependencias
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener productos con filtros avanzados y paginación
    
    - **Filtros múltiples**: Combina varios criterios de búsqueda
    - **Paginación**: Control total sobre página y tamaño
    - **Ordenamiento**: Por cualquier campo en orden ascendente o descendente
    - **Caché**: Resultados cacheados para mejor performance
    """
    # Crear objetos de filtros y paginación
    filters = ProductoFilters(
        nombre=nombre,
        codigo_barras=codigo_barras,
        principio_activo=principio_activo,
        id_laboratorio=id_laboratorio,
        id_seccion=id_seccion,
        precio_min=precio_min,
        precio_max=precio_max,
        stock_min=stock_min,
        stock_max=stock_max,
        stock_bajo=stock_bajo,
        requiere_receta=requiere_receta,
        estado=estado,
        forma_farmaceutica=forma_farmaceutica
    )
    
    pagination = PaginationParams(page=page, size=size)
    
    # Generar clave de caché
    cache_key = f"productos:advanced:{filters.model_dump_json()}:{pagination.model_dump_json()}:{sort_by}:{order}"
    
    # Intentar obtener del caché
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return cached_result
    
    # Obtener datos de la base de datos
    result = get_productos_advanced(db, filters, pagination, sort_by, order)
    
    # Cachear resultado por 5 minutos
    cache_manager.set(cache_key, result, ttl=300)
    
    return result


@router.get("/search", response_model=dict)
async def search_productos(
    q: str = Query(..., min_length=2, description="Término de búsqueda"),
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(50, ge=1, le=100, description="Elementos por página"),
    id_laboratorio: Optional[int] = Query(None, description="Filtrar por laboratorio"),
    id_seccion: Optional[int] = Query(None, description="Filtrar por sección"),
    estado: Optional[str] = Query("Activo", description="Estado del producto"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Búsqueda avanzada de productos
    
    Busca en múltiples campos:
    - Nombre del producto
    - Principio activo
    - Descripción
    - Código de barras
    - Forma farmacéutica
    """
    pagination = PaginationParams(page=page, size=size)
    
    filters = ProductoFilters(
        id_laboratorio=id_laboratorio,
        id_seccion=id_seccion,
        estado=estado
    )
    
    # Generar clave de caché
    cache_key = f"productos:search:{q}:{filters.model_dump_json()}:{pagination.model_dump_json()}"
    
    # Intentar obtener del caché
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return cached_result
    
    # Buscar en la base de datos
    result = search_productos_advanced(db, q, pagination, filters)
    
    # Cachear resultado por 3 minutos
    cache_manager.set(cache_key, result, ttl=180)
    
    return result


@router.get("/stats", response_model=dict)
async def get_stats(
    id_laboratorio: Optional[int] = Query(None, description="Filtrar por laboratorio"),
    id_seccion: Optional[int] = Query(None, description="Filtrar por sección"),
    estado: Optional[str] = Query("Activo", description="Estado del producto"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de productos
    
    Retorna:
    - Total de productos
    - Productos activos/inactivos
    - Productos con stock bajo
    - Valor total del inventario
    - Stock total
    - Precio promedio
    - Porcentaje de productos con stock bajo
    """
    filters = ProductoFilters(
        id_laboratorio=id_laboratorio,
        id_seccion=id_seccion,
        estado=estado
    )
    
    # Generar clave de caché
    cache_key = f"productos:stats:{filters.model_dump_json()}"
    
    # Intentar obtener del caché
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return {
            "success": True,
            "message": "Estadísticas obtenidas exitosamente",
            "data": cached_result
        }
    
    # Obtener estadísticas
    stats = get_productos_stats(db, filters)
    
    # Cachear resultado por 5 minutos
    cache_manager.set(cache_key, stats, ttl=300)
    
    return {
        "success": True,
        "message": "Estadísticas obtenidas exitosamente",
        "data": stats
    }


@router.get("/top", response_model=dict)
async def get_top(
    limit: int = Query(10, ge=1, le=50, description="Número de productos"),
    criterio: str = Query("stock", pattern="^(stock|precio|nombre|stock_bajo)$", description="Criterio de ordenamiento"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener top productos según criterio
    
    Criterios disponibles:
    - **stock**: Productos con mayor stock
    - **precio**: Productos más caros
    - **nombre**: Orden alfabético
    - **stock_bajo**: Productos con stock más bajo
    """
    # Generar clave de caché
    cache_key = f"productos:top:{limit}:{criterio}"
    
    # Intentar obtener del caché
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return {
            "success": True,
            "message": f"Top {limit} productos obtenidos exitosamente",
            "data": cached_result
        }
    
    # Obtener top productos
    productos = get_top_productos(db, limit, criterio)
    
    # Convertir a diccionarios
    productos_dict = [
        {
            "id_producto": p.id_producto,
            "nombre_producto": p.nombre_producto,
            "stock_actual": p.stock_actual,
            "stock_minimo": p.stock_minimo,
            "precio_compra": p.precio_compra,
            "laboratorio": p.laboratorio.nombre_laboratorio if p.laboratorio else None,
            "seccion": p.seccion.nombre_seccion if p.seccion else None
        }
        for p in productos
    ]
    
    # Cachear resultado por 10 minutos
    cache_manager.set(cache_key, productos_dict, ttl=600)
    
    return {
        "success": True,
        "message": f"Top {limit} productos obtenidos exitosamente",
        "data": productos_dict
    }


@router.get("/stats/por-laboratorio", response_model=dict)
async def get_stats_por_laboratorio(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de productos agrupados por laboratorio
    
    Retorna para cada laboratorio:
    - Total de productos
    - Stock total
    - Valor total del inventario
    """
    # Generar clave de caché
    cache_key = "productos:stats:por_laboratorio"
    
    # Intentar obtener del caché
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return {
            "success": True,
            "message": "Estadísticas por laboratorio obtenidas exitosamente",
            "data": cached_result
        }
    
    # Obtener estadísticas
    stats = get_productos_por_laboratorio_stats(db)
    
    # Cachear resultado por 10 minutos
    cache_manager.set(cache_key, stats, ttl=600)
    
    return {
        "success": True,
        "message": "Estadísticas por laboratorio obtenidas exitosamente",
        "data": stats
    }


@router.get("/stats/por-seccion", response_model=dict)
async def get_stats_por_seccion(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de productos agrupados por sección
    
    Retorna para cada sección:
    - Total de productos
    - Stock total
    - Valor total del inventario
    """
    # Generar clave de caché
    cache_key = "productos:stats:por_seccion"
    
    # Intentar obtener del caché
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        return {
            "success": True,
            "message": "Estadísticas por sección obtenidas exitosamente",
            "data": cached_result
        }
    
    # Obtener estadísticas
    stats = get_productos_por_seccion_stats(db)
    
    # Cachear resultado por 10 minutos
    cache_manager.set(cache_key, stats, ttl=600)
    
    return {
        "success": True,
        "message": "Estadísticas por sección obtenidas exitosamente",
        "data": stats
    }


@router.post("/cache/clear", response_model=MessageResponse)
async def clear_productos_cache(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Limpiar caché de productos (requiere autenticación)
    
    Útil después de operaciones masivas de actualización
    """
    # Verificar que el usuario tenga permisos (admin)
    if not hasattr(current_user, 'rol') or current_user.rol.nombre_rol != 'admin':
        raise HTTPException(status_code=403, detail="No tiene permisos para esta operación")
    
    # Limpiar caché de productos
    deleted = cache_manager.delete_pattern("productos:*")
    
    return MessageResponse(
        success=True,
        message=f"Caché de productos limpiado exitosamente ({deleted} claves eliminadas)"
    )


@router.get("/cache/stats", response_model=dict)
async def get_cache_stats(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtener estadísticas del caché
    
    Retorna información sobre el uso del caché Redis
    """
    stats = cache_manager.get_stats()
    
    return {
        "success": True,
        "message": "Estadísticas de caché obtenidas exitosamente",
        "data": stats
    }
