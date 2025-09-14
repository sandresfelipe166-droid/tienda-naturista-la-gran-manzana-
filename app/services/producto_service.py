from sqlalchemy.orm import Session
from app.models.models import Producto, Seccion, Laboratorio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from app.utils import calcular_dias_para_vencer
from app.core.logging_config import get_logger

logger = get_logger()

class ProductoService:
    @staticmethod
    def listar(db: Session, page: int, size: int, filtros: Dict[str, Any]) -> Tuple[List[Producto], int]:
        query = db.query(Producto)
        for attr, value in filtros.items():
            query = query.filter(getattr(Producto, attr) == value)
        total = query.count()
        productos = query.offset((page - 1) * size).limit(size).all()

        # Calculate dias_para_vencer for each producto
        for producto in productos:
            producto.dias_para_vencer = calcular_dias_para_vencer(getattr(producto, "fecha_vencimiento", None))

        return productos, total

    @staticmethod
    def obtener_por_id(db: Session, id_producto: int) -> Optional[Producto]:
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
        if producto:
            producto.dias_para_vencer = calcular_dias_para_vencer(getattr(producto, "fecha_vencimiento", None))
        return producto

    @staticmethod
    def crear(db: Session, data: Dict[str, Any]) -> Producto:
        try:
            # Validar que la sección exista
            if 'id_seccion' in data:
                seccion = db.query(Seccion).filter(Seccion.id_seccion == data['id_seccion']).first()
                if not seccion:
                    raise ValueError("La sección especificada no existe")

            # Validar que el laboratorio exista
            if 'id_laboratorio' in data:
                laboratorio = db.query(Laboratorio).filter(Laboratorio.id_laboratorio == data['id_laboratorio']).first()
                if not laboratorio:
                    raise ValueError("El laboratorio especificado no existe")

            nuevo_producto = Producto(**data)
            db.add(nuevo_producto)
            db.commit()
            db.refresh(nuevo_producto)
            return nuevo_producto
        except Exception as e:
            logger.error(f"Error creating product: {e}", extra={"data": data})
            db.rollback()
            raise

    @staticmethod
    def actualizar(db: Session, id_producto: int, updates: Dict[str, Any]) -> Producto:
        try:
            producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
            if not producto:
                return None

            # Validar seccion
            id_seccion_to_check = updates.get('id_seccion', producto.id_seccion)
            if id_seccion_to_check is not None:
                seccion = db.query(Seccion).filter(Seccion.id_seccion == id_seccion_to_check).first()
                if not seccion:
                    raise ValueError("La sección especificada no existe")

            # Validar laboratorio
            id_laboratorio_to_check = updates.get('id_laboratorio', producto.id_laboratorio)
            if id_laboratorio_to_check is not None:
                laboratorio = db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio_to_check).first()
                if not laboratorio:
                    raise ValueError("El laboratorio especificado no existe")

            # Update only the provided fields
            db.query(Producto).filter(Producto.id_producto == id_producto).update(updates)
            db.commit()
            # Return the updated product
            return db.query(Producto).filter(Producto.id_producto == id_producto).first()
        except Exception as e:
            logger.error(f"Error updating product {id_producto}: {e}", extra={"updates": updates})
            db.rollback()
            raise

    @staticmethod
    def eliminar(db: Session, id_producto: int, modo: str = "logico") -> bool:
        try:
            producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
            if not producto:
                return False
            if modo == "logico":
                producto.estado = "Inactivo"
            elif modo == "fisico":
                db.delete(producto)
            else:
                raise ValueError("Modo de eliminación inválido")
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting product {id_producto}: {e}", extra={"modo": modo})
            db.rollback()
            raise

    @staticmethod
    def get_productos(db: Session, skip: int = 0, limit: int = 100, nombre: Optional[str] = None, id_seccion: Optional[int] = None, id_laboratorio: Optional[int] = None, estado: Optional[str] = "Activo") -> List[Producto]:
        query = db.query(Producto)
        if nombre:
            query = query.filter(Producto.nombre_producto.ilike(f"%{nombre}%"))
        if id_seccion:
            query = query.filter(Producto.id_seccion == id_seccion)
        if id_laboratorio:
            query = query.filter(Producto.id_laboratorio == id_laboratorio)
        if estado:
            query = query.filter(Producto.estado == estado)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_productos(db: Session, nombre: Optional[str] = None, id_seccion: Optional[int] = None, id_laboratorio: Optional[int] = None, estado: Optional[str] = "Activo") -> int:
        query = db.query(Producto)
        if nombre:
            query = query.filter(Producto.nombre_producto.ilike(f"%{nombre}%"))
        if id_seccion:
            query = query.filter(Producto.id_seccion == id_seccion)
        if id_laboratorio:
            query = query.filter(Producto.id_laboratorio == id_laboratorio)
        if estado:
            query = query.filter(Producto.estado == estado)
        return query.count()

    @staticmethod
    def search_productos(db: Session, q: str, skip: int = 0, limit: int = 50) -> List[Producto]:
        query = db.query(Producto).filter(Producto.nombre_producto.ilike(f"%{q}%"))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_productos_bajo_stock(db: Session) -> List[Producto]:
        return db.query(Producto).filter(Producto.stock_actual <= Producto.stock_minimo).all()

    @staticmethod
    def get_productos_por_vencer(db: Session, dias: int) -> List[Producto]:
        # Assuming fecha_vencimiento exists
        from datetime import datetime, timedelta
        fecha_limite = datetime.now() + timedelta(days=dias)
        return db.query(Producto).filter(Producto.fecha_vencimiento <= fecha_limite).all()

    @staticmethod
    def get_producto_by_id(db: Session, producto_id: int) -> Optional[Producto]:
        return ProductoService.obtener_por_id(db, producto_id)

    @staticmethod
    def create_producto(db: Session, producto) -> Producto:
        return ProductoService.crear(db, producto.model_dump())

    @staticmethod
    def update_producto(db: Session, producto_id: int, producto_update) -> Producto:
        return ProductoService.actualizar(db, producto_id, producto_update.model_dump())

    @staticmethod
    def delete_producto(db: Session, producto_id: int, modo: str = "logico") -> bool:
        return ProductoService.eliminar(db, producto_id, modo)
