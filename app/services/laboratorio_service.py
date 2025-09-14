from sqlalchemy.orm import Session
from app.models.models import Laboratorio
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

class LaboratorioService:
    @staticmethod
    def listar(db: Session, page: int, size: int, filtros: Dict[str, Any]) -> Tuple[List[Laboratorio], int]:
        query = db.query(Laboratorio)
        for attr, value in filtros.items():
            query = query.filter(getattr(Laboratorio, attr) == value)
        total = query.count()
        laboratorios = query.offset((page - 1) * size).limit(size).all()
        return laboratorios, total

    @staticmethod
    def obtener_por_id(db: Session, id_laboratorio: int) -> Optional[Laboratorio]:
        return db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()

    @staticmethod
    def crear(db: Session, data: Dict[str, Any]) -> int:
        nuevo_laboratorio = Laboratorio(**data)
        db.add(nuevo_laboratorio)
        db.commit()
        db.refresh(nuevo_laboratorio)
        return nuevo_laboratorio.id_laboratorio

    @staticmethod
    def actualizar(db: Session, id_laboratorio: int, updates: Dict[str, Any]) -> bool:
        laboratorio = db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()
        if not laboratorio:
            return False
        for key, value in updates.items():
            setattr(laboratorio, key, value)
        db.commit()
        return True

    @staticmethod
    def eliminar(db: Session, id_laboratorio: int, modo: str = "logico") -> bool:
        laboratorio = db.query(Laboratorio).filter(Laboratorio.id_laboratorio == id_laboratorio).first()
        if not laboratorio:
            return False
        if modo == "logico":
            laboratorio.estado = "Inactivo"
        elif modo == "fisico":
            db.delete(laboratorio)
        else:
            raise ValueError("Modo de eliminación inválido")
        db.commit()
        return True
