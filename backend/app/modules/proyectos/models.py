"""
Modelos de base de datos para el módulo de Proyectos.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Numeric, Enum, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class EstadoProyecto(str, PyEnum):
    """Estados posibles de un proyecto"""
    PROSPECTO = "prospecto"
    COTIZACION = "cotizacion"
    APROBADO = "aprobado"
    EN_PROGRESO = "en_progreso"
    PAUSADO = "pausado"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


class Proyecto(Base):
    """
    Modelo de Proyecto de construcción.

    Representa un proyecto individual con su presupuesto,
    fechas y estado actual.
    """
    __tablename__ = "proyectos"

    # Identificadores
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    codigo = Column(String(50), unique=True, nullable=False, index=True)

    # Información básica
    nombre = Column(String(200), nullable=False)
    cliente = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)

    # Fechas
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin_estimada = Column(DateTime, nullable=True)
    fecha_fin_real = Column(DateTime, nullable=True)

    # Financiero
    presupuesto_total = Column(Numeric(precision=12, scale=2), nullable=False)
    horas_presupuestadas = Column(Numeric(precision=10, scale=2), nullable=True)

    # Estado
    estado = Column(Enum(EstadoProyecto), default=EstadoProyecto.PROSPECTO, nullable=False)

    # Metadata adicional (JSON flexible)
    datos_adicionales = Column(JSON, nullable=True)

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones (se agregarán en fases posteriores)
    # costos = relationship("Costo", back_populates="proyecto")
    # tareas = relationship("Tarea", back_populates="proyecto")
    # presupuesto_lineas = relationship("PresupuestoLinea", back_populates="proyecto")
    # registro_horas = relationship("RegistroHoras", back_populates="proyecto")

    def __repr__(self):
        return f"<Proyecto(codigo='{self.codigo}', nombre='{self.nombre}', estado='{self.estado}')>"

    @property
    def dias_transcurridos(self) -> int | None:
        """Calcula los días transcurridos desde el inicio del proyecto"""
        if self.fecha_inicio:
            return (datetime.utcnow() - self.fecha_inicio).days
        return None

    @property
    def dias_restantes(self) -> int | None:
        """Calcula los días restantes hasta la fecha de fin estimada"""
        if self.fecha_fin_estimada:
            return (self.fecha_fin_estimada - datetime.utcnow()).days
        return None
