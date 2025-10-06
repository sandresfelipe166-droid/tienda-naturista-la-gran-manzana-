from sqlalchemy.orm import Session
from app.models.models import Producto, Seccion, Laboratorio
from typing import List, Optional, Dict, Any, Tuple
from app.core.logging_config import get_logger
from app.crud.producto import (
    get_productos, count_productos, search_productos,
    get_productos_bajo_stock, get_productos_por_vencer,
    get_producto_by_id, create_producto, update_producto, delete_producto,
    get_total_productos_activos, get_valor_total_stock, count_productos_bajo_stock
)

logger = get_logger()

class ProductoService:
    @staticmethod
    def listar(db: Session, page: int, size: int, filtros: Dict[str, Any]) -> Tuple[List[Producto], int]:
        query = db.query(Producto)
        for attr, value in filtros.items():
            query = query.filter(getattr(Producto, attr) == value)
        total = query.count()
        productos = query.offset((page - 1) * size).limit(size).all()
        return productos, total

    @staticmethod
    def obtener_por_id(db: Session, id_producto: int) -> Optional[Producto]:
        producto = db.query(Producto).filter(Producto.id_producto == id_producto).first()
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
            logger.error("Error creating product: %s", e, extra={"data": data})
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
            logger.error("Error updating product %s: %s", id_producto, e, extra={"updates": updates})
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
            logger.error("Error deleting product %s: %s", id_producto, e, extra={"modo": modo})
            db.rollback()
            raise

    @staticmethod
    def get_productos(db: Session, skip: int = 0, limit: int = 100, nombre: Optional[str] = None, id_seccion: Optional[int] = None, id_laboratorio: Optional[int] = None, estado: Optional[str] = "Activo") -> List[Producto]:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return get_productos(db, skip, limit, nombre, id_seccion, id_laboratorio, estado)

    @staticmethod
    def count_productos(db: Session, nombre: Optional[str] = None, id_seccion: Optional[int] = None, id_laboratorio: Optional[int] = None, estado: Optional[str] = "Activo") -> int:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return count_productos(db, nombre, id_seccion, id_laboratorio, estado)

    @staticmethod
    def search_productos(db: Session, q: str, skip: int = 0, limit: int = 50) -> List[Producto]:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return search_productos(db, q, skip, limit)

    @staticmethod
    def get_productos_bajo_stock(db: Session) -> List[Producto]:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return get_productos_bajo_stock(db)

    @staticmethod
    def get_total_productos_activos(db: Session) -> int:
        """Contar productos activos"""
        return get_total_productos_activos(db)

    @staticmethod
    def get_valor_total_stock(db: Session) -> float:
        """Calcular el valor total del stock"""
        return get_valor_total_stock(db)

    @staticmethod
    def count_productos_bajo_stock(db: Session) -> int:
        """Contar productos con stock bajo"""
        return count_productos_bajo_stock(db)

    @staticmethod
    def get_productos_por_vencer(db: Session, dias: int) -> List[Producto]:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return get_productos_por_vencer(db, dias)

    @staticmethod
    def get_producto_by_id(db: Session, producto_id: int) -> Optional[Producto]:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return get_producto_by_id(db, producto_id)

    @staticmethod
    def create_producto(db: Session, producto) -> Producto:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return create_producto(db, producto)

    @staticmethod
    def update_producto(db: Session, producto_id: int, producto_update) -> Producto:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return update_producto(db, producto_id, producto_update)

    @staticmethod
    def delete_producto(db: Session, producto_id: int, modo: str = "logico") -> bool:
        """Delegar a CRUD - método mantenido por compatibilidad"""
        return delete_producto(db, producto_id, modo == "logico")

    @staticmethod
    def buscar_productos(db: Session, q: str, skip: int = 0, limit: int = 50) -> List[Producto]:
        """Buscar productos por query string"""
        return search_productos(db, q, skip, limit)
