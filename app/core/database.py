from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy import event
import logging
import time
from contextlib import contextmanager
from typing import Generator
from app.core.config import settings
from app.core.logging_config import inventario_logger

logger = inventario_logger

# Configurar logging para SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)

# Motor de base de datos con configuración avanzada
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,
    connect_args=settings.db_connect_args,
    future=True  # Habilitar SQLAlchemy 2.0 features
)

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
            query=statement[:100] + "..." if len(statement) > 100 else statement
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
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# Base para modelos
Base = declarative_base()

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
                    return {
                        "status": "healthy",
                        "message": "Database connection successful"
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "message": "Database query failed"
                    }
        except Exception as e:
            logger.log_error(e, {"context": "health_check"})
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }

    def get_connection_info(self) -> dict:
        """Obtener información de la conexión"""
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "checked_out": pool.checkedout()
        }

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

# Función de compatibilidad para obtener sesión de DB
def get_database():
    return db_manager.get_session()

# Función para obtener información de la base de datos
def get_db_info():
    return db_manager.get_connection_info()
