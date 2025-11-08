from typing import Any, cast

from sqlalchemy.orm import Session

from app.models.models import Alerta, Seccion


class SeccionService:
    @staticmethod
    def listar(
        db: Session, page: int, size: int, filtros: dict[str, Any]
    ) -> tuple[list[Seccion], int]:
        query = db.query(Seccion)
        for attr, value in filtros.items():
            query = query.filter(getattr(Seccion, attr) == value)
        total = query.count()
        secciones = query.offset((page - 1) * size).limit(size).all()
        return secciones, total

    @staticmethod
    def obtener_por_id(db: Session, id_seccion: int) -> Seccion | None:
        return db.query(Seccion).filter(Seccion.id_seccion == id_seccion).first()

    @staticmethod
    def crear(db: Session, data: dict[str, Any]) -> int:
        nueva_seccion = Seccion(**data)
        db.add(nueva_seccion)
        db.commit()
        db.refresh(nueva_seccion)
        # Help static type checkers that view SQLAlchemy columns as Column[int]
        return int(cast(Any, nueva_seccion).id_seccion)

    @staticmethod
    def actualizar(db: Session, id_seccion: int, updates: dict[str, Any]) -> bool:
        seccion = db.query(Seccion).filter(Seccion.id_seccion == id_seccion).first()
        if not seccion:
            return False
        for key, value in updates.items():
            setattr(seccion, key, value)
        db.commit()
        return True

    @staticmethod
    def eliminar(db: Session, id_seccion: int, modo: str = "logico") -> bool:
        seccion = db.query(Seccion).filter(Seccion.id_seccion == id_seccion).first()
        if not seccion:
            return False
        if modo == "logico":
            # Cast to Any to satisfy static type checkers (Column[str] attribute)
            cast(Any, seccion).estado = "Inactivo"
        elif modo == "fisico":
            db.delete(seccion)
        else:
            raise ValueError("Modo de eliminación inválido")
        db.commit()
        return True


class AlertaService:
    @staticmethod
    def listar(
        db: Session, page: int, size: int, filtros: dict[str, Any]
    ) -> tuple[list[Alerta], int]:
        query = db.query(Alerta)
        for attr, value in filtros.items():
            query = query.filter(getattr(Alerta, attr) == value)
        total = query.count()
        alertas = query.offset((page - 1) * size).limit(size).all()
        return alertas, total

    @staticmethod
    def obtener_por_id(db: Session, id_alerta: int) -> Alerta | None:
        return db.query(Alerta).filter(Alerta.id_alerta == id_alerta).first()

    @staticmethod
    def crear(db: Session, data: dict[str, Any]) -> int:
        nueva_alerta = Alerta(**data)
        db.add(nueva_alerta)
        db.commit()
        db.refresh(nueva_alerta)
        # Help static type checkers that view SQLAlchemy columns as Column[int]
        return int(cast(Any, nueva_alerta).id_alerta)

    @staticmethod
    def actualizar(db: Session, id_alerta: int, updates: dict[str, Any]) -> bool:
        alerta = db.query(Alerta).filter(Alerta.id_alerta == id_alerta).first()
        if not alerta:
            return False
        for key, value in updates.items():
            setattr(alerta, key, value)
        db.commit()
        return True

    @staticmethod
    def eliminar(db: Session, id_alerta: int, modo: str = "logico") -> bool:
        alerta = db.query(Alerta).filter(Alerta.id_alerta == id_alerta).first()
        if not alerta:
            return False
        if modo == "logico":
            # Cast to Any to satisfy static type checkers (Column[str] attribute)
            cast(Any, alerta).estado = "Inactivo"
        elif modo == "fisico":
            db.delete(alerta)
        else:
            raise ValueError("Modo de eliminación inválido")
        db.commit()
        return True
