"""
Modelos de Tareas
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base


class EstadoTarea(str, PyEnum):
    """Estados posibles de una tarea"""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class PrioridadTarea(str, PyEnum):
    """Prioridades de tareas"""
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class Tarea(Base):
    """Modelo de Tarea"""
    __tablename__ = "tareas"

    # Identificadores
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proyecto_id = Column(String(36), ForeignKey("proyectos.id"), nullable=False, index=True)
    asignado_a_id = Column(String(36), ForeignKey("usuarios.id"), nullable=True, index=True)
    creado_por_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False, index=True)

    # Información de la tarea
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(String(20), default=EstadoTarea.PENDIENTE.value, nullable=False, index=True)
    prioridad = Column(String(20), default=PrioridadTarea.MEDIA.value, nullable=False, index=True)

    # Fechas
    fecha_vencimiento = Column(DateTime, nullable=True)
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_completada = Column(DateTime, nullable=True)

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    proyecto = relationship("Proyecto", foreign_keys=[proyecto_id], backref="tareas")
    asignado_a = relationship("Usuario", foreign_keys=[asignado_a_id], backref="tareas_asignadas")
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id], backref="tareas_creadas")

    # Índices compuestos
    __table_args__ = (
        Index('idx_tarea_proyecto_estado', 'proyecto_id', 'estado'),
        Index('idx_tarea_asignado_estado', 'asignado_a_id', 'estado'),
        Index('idx_tarea_vencimiento', 'fecha_vencimiento'),
    )

    @property
    def esta_vencida(self) -> bool:
        """Verifica si la tarea está vencida"""
        if not self.fecha_vencimiento:
            return False
        if self.estado in [EstadoTarea.COMPLETADA.value, EstadoTarea.CANCELADA.value]:
            return False
        return datetime.utcnow() > self.fecha_vencimiento

    @property
    def dias_hasta_vencimiento(self) -> int:
        """Calcula los días hasta el vencimiento (negativo si está vencida)"""
        if not self.fecha_vencimiento:
            return 0
        return (self.fecha_vencimiento - datetime.utcnow()).days

    @property
    def esta_completada(self) -> bool:
        """Verifica si la tarea está completada"""
        return self.estado == EstadoTarea.COMPLETADA.value

    @property
    def duracion_dias(self) -> int:
        """Calcula la duración de la tarea en días"""
        if not self.fecha_inicio:
            return 0
        fecha_fin = self.fecha_completada if self.fecha_completada else datetime.utcnow()
        return (fecha_fin - self.fecha_inicio).days

    def __repr__(self):
        return f"<Tarea {self.titulo} - {self.estado}>"
