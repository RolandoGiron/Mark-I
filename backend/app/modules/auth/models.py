"""
Modelos de base de datos para el módulo de Autenticación.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Boolean, Enum

from app.database import Base


class RolUsuario(str, PyEnum):
    """Roles de usuario en el sistema"""
    ADMIN = "admin"
    GERENTE = "gerente"
    SUPERVISOR = "supervisor"
    TRABAJADOR = "trabajador"


class Usuario(Base):
    """
    Modelo de Usuario del sistema.

    Maneja autenticación y autorización.
    """
    __tablename__ = "usuarios"

    # Identificadores
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Credenciales
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)

    # Información personal
    nombre_completo = Column(String(200), nullable=False)
    telefono = Column(String(20), nullable=True)

    # Telegram integration
    telegram_id = Column(String(50), unique=True, nullable=True, index=True)
    telegram_username = Column(String(100), nullable=True)

    # Autorización
    rol = Column(Enum(RolUsuario), default=RolUsuario.TRABAJADOR, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ultimo_acceso = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Usuario(username='{self.username}', rol='{self.rol}')>"

    @property
    def es_admin(self) -> bool:
        """Indica si el usuario es administrador"""
        return self.rol == RolUsuario.ADMIN

    @property
    def puede_validar_gastos(self) -> bool:
        """Indica si el usuario puede validar gastos"""
        return self.rol in [RolUsuario.ADMIN, RolUsuario.GERENTE, RolUsuario.SUPERVISOR]
