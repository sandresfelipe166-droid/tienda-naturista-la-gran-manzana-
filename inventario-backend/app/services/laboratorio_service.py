from typing import Any, cast

from sqlalchemy.orm import Session

from app.models.models import Laboratorio


class LaboratorioService:
    @staticmethod
    def listar(
        db: Session, page: int, size: int, filtros: dict[str, Any]
    ) -> tuple[list[Laboratorio], int]:
        query = db.query(Laboratorio)
        for attr, value in filtros.items():
            query = query.filter(getattr(Laboratorio, attr) == value)
        total = query.count()
        laboratorios = query.offset((page - 1) * size).limit(size).all()
        return laboratorios, total

    @staticmethod
    def obtener_por_id(db: Session, id_laboratorio: int) -> Laboratorio | None:
        return db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()

    @staticmethod
    def crear(db: Session, data: dict[str, Any]) -> int:
        nuevo_laboratorio = Laboratorio(**data)
        db.add(nuevo_laboratorio)
        db.commit()
        db.refresh(nuevo_laboratorio)
        # Cast to satisfy static type checkers that see Column[int]
        return int(cast(Any, nuevo_laboratorio).id_laboratorio)

    @staticmethod
    def actualizar(db: Session, id_laboratorio: int, updates: dict[str, Any]) -> bool:
        laboratorio = (
            db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()
        )
        if not laboratorio:
            return False
        for key, value in updates.items():
            setattr(laboratorio, key, value)
        db.commit()
        return True

    @staticmethod
    def eliminar(db: Session, id_laboratorio: int, modo: str = "logico") -> bool:
        laboratorio = (
            db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()
        )
        if not laboratorio:
            return False
        if modo == "logico":
            # Help static type checkers by using cast to Any
            cast(Any, laboratorio).estado = "Inactivo"
        elif modo == "fisico":
            db.delete(laboratorio)
        else:
            raise ValueError("Modo de eliminación inválido")
        db.commit()
        return True
