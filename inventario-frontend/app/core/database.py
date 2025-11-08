import logging
import time
from collections.abc import Generator

from sqlalchemy import event, text

from app.core.logging_config import inventario_logger
from app.models.database import SessionLocal as SharedSessionLocal
from app.models.database import engine as shared_engine

logger = inventario_logger

# Configurar logging para SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)

# Motor de base de datos con configuración avanzada
engine = shared_engine


# Configurar eventos de SQLAlchemy para logging
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()


@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 1.0:  # Log queries que toman más de 1 segundo
        logger.log_database_operation(
            operation="slow_query",
            table="unknown",
            duration=total,
            query=statement[:100] + "..." if len(statement) > 100 else statement,
        )


@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    logger.log_database_operation("connect", "database")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    logger.log_database_operation("checkout", "pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_connection, connection_record):
    logger.log_database_operation("checkin", "pool")


# Sesión de base de datos
SessionLocal = SharedSessionLocal

# Base imported from app.models.database


class DatabaseManager:
    """Gestor avanzado de base de datos con retry y health checks"""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def get_session(self) -> Generator:
        """Obtener sesión de base de datos con manejo de errores"""
        db = None
        try:
            db = SessionLocal()
            yield db
        except Exception as e:
            logger.log_error(e, {"context": "database_session"})
            if db:
                db.rollback()
            raise
        finally:
            if db:
                db.close()

    def health_check(self) -> dict:
        """Verificar estado de la base de datos"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as health_check"))
                row = result.fetchone()
                if row and row[0] == 1:
                    return {"status": "healthy", "message": "Database connection successful"}
                else:
                    return {"status": "unhealthy", "message": "Database query failed"}
        except Exception as e:
            logger.log_error(e, {"context": "health_check"})
            return {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}

    def get_connection_info(self) -> dict:
        """Obtener información de la conexión"""
        pool = engine.pool
        return {
            "pool_size": pool.size(),  # type: ignore[attr-defined]
            "checked_in": pool.checkedin(),  # type: ignore[attr-defined]
            "checked_out": pool.checkedout(),  # type: ignore[attr-defined]
            "overflow": pool.overflow(),  # type: ignore[attr-defined]
        }


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()


# Función de compatibilidad para obtener sesión de DB
def get_database():
    return db_manager.get_session()


# Función para obtener información de la base de datos
def get_db_info():
    return db_manager.get_connection_info()
