"""
Configuración de la base de datos con SQLAlchemy.
Soporta SQLite (desarrollo) y PostgreSQL (producción).
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

# Configuración del engine según el tipo de base de datos
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite requiere check_same_thread=False para uso con FastAPI
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=settings.DEBUG  # Log de queries SQL en modo debug
    )
else:
    # PostgreSQL
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Verificar conexión antes de usar
        pool_size=10,        # Tamaño del pool de conexiones
        max_overflow=20,     # Conexiones adicionales si se necesitan
        echo=settings.DEBUG
    )

# SessionLocal: Factory para crear sesiones de DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Clase base para todos los modelos
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener una sesión de base de datos.
    Se usa como dependency en las rutas de FastAPI.

    Uso:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas.
    Solo para desarrollo/testing. En producción usar Alembic.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Elimina todas las tablas de la base de datos.
    PELIGROSO: Solo usar en desarrollo/testing.
    """
    Base.metadata.drop_all(bind=engine)
