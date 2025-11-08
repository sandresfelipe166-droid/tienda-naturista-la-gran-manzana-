"""
Optimizador de queries con eager loading para eliminar N+1 queries.
"""
from typing import TYPE_CHECKING

from sqlalchemy.orm import Query, joinedload, selectinload

if TYPE_CHECKING:
    from sqlalchemy.orm.strategy_options import _AbstractLoad


class QueryOptimizer:
    """
    Clase helper para optimizar queries con eager loading estratégico.
    
    Uso:
        query = QueryOptimizer.optimize_producto_query(db.query(Producto))
        productos = query.all()  # Sin N+1 queries!
    """

    @staticmethod
    def optimize_producto_query(query: Query) -> Query:
        """
        Optimiza query de productos con eager loading de relaciones.
        Elimina N+1 queries al cargar seccion, laboratorio, lotes.
        """
        return query.options(
            joinedload("seccion"),  # type: ignore[arg-type]
            joinedload("laboratorio"),  # type: ignore[arg-type]
            selectinload("lotes"),  # type: ignore[arg-type]
            selectinload("alertas"),  # type: ignore[arg-type]
        )

    @staticmethod
    def optimize_venta_query(query: Query) -> Query:
        """
        Optimiza query de ventas con eager loading de detalles y relaciones.
        """
        return query.options(
            joinedload("usuario"),  # type: ignore[arg-type]
            joinedload("cliente"),  # type: ignore[arg-type]
            selectinload("detalles").joinedload("lote").joinedload("producto"),  # type: ignore[arg-type]
        )

    @staticmethod
    def optimize_entrada_query(query: Query) -> Query:
        """
        Optimiza query de entradas.
        """
        return query.options(
            joinedload("usuario"),  # type: ignore[arg-type]
            joinedload("lote").joinedload("producto"),  # type: ignore[arg-type]
        )

    @staticmethod
    def optimize_salida_query(query: Query) -> Query:
        """
        Optimiza query de salidas.
        """
        return query.options(
            joinedload("usuario"),  # type: ignore[arg-type]
            joinedload("lote").joinedload("producto"),  # type: ignore[arg-type]
        )

    @staticmethod
    def optimize_alerta_query(query: Query) -> Query:
        """
        Optimiza query de alertas.
        """
        return query.options(
            joinedload("producto").joinedload("seccion"),  # type: ignore[arg-type]
            joinedload("producto").joinedload("laboratorio"),  # type: ignore[arg-type]
            joinedload("seccion"),  # type: ignore[arg-type]
        )

    @staticmethod
    def optimize_cotizacion_query(query: Query) -> Query:
        """
        Optimiza query de cotizaciones.
        """
        return query.options(
            joinedload("usuario"),  # type: ignore[arg-type]
            joinedload("cliente"),  # type: ignore[arg-type]
            selectinload("detalles").joinedload("producto"),  # type: ignore[arg-type]
        )

    @staticmethod
    def optimize_gasto_query(query: Query) -> Query:
        """
        Optimiza query de gastos.
        """
        return query.options(
            joinedload("usuario"),  # type: ignore[arg-type]
        )


# Decorator para aplicar optimización automática
def with_optimized_query(optimizer_method):
    """
    Decorator para aplicar optimización de query automáticamente.
    
    Uso:
        @with_optimized_query(QueryOptimizer.optimize_producto_query)
        def get_productos(db: Session):
            return db.query(Producto).all()
    """

    def decorator(func):
        def wrapper(db, *args, **kwargs):
            # Intercept query creation
            original_query = db.query
            
            def optimized_query(*q_args, **q_kwargs):
                query = original_query(*q_args, **q_kwargs)
                return optimizer_method(query)
            
            db.query = optimized_query
            try:
                return func(db, *args, **kwargs)
            finally:
                db.query = original_query
        
        return wrapper
    
    return decorator
