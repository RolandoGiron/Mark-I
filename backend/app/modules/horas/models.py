"""
Modelos de Horas
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Date, Index, Text
from sqlalchemy.orm import relationship
from app.database import Base


class RegistroHora(Base):
    """Modelo de Registro de Horas"""
    __tablename__ = "registros_horas"

    # Identificadores
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    empleado_id = Column(String(36), ForeignKey("empleados.id"), nullable=False, index=True)
    proyecto_id = Column(String(36), ForeignKey("proyectos.id"), nullable=False, index=True)
    tarea_id = Column(String(36), ForeignKey("tareas.id"), nullable=True, index=True)

    # Datos del registro
    fecha = Column(Date, nullable=False, index=True)
    horas = Column(Numeric(precision=5, scale=2), nullable=False)  # Permite valores como 7.5, 8.25
    descripcion = Column(Text, nullable=True)

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    empleado = relationship("Empleado", foreign_keys=[empleado_id], backref="registros_horas")
    proyecto = relationship("Proyecto", foreign_keys=[proyecto_id], backref="registros_horas")
    tarea = relationship("Tarea", foreign_keys=[tarea_id], backref="registros_horas")

    # Índices compuestos
    __table_args__ = (
        Index('idx_registro_empleado_fecha', 'empleado_id', 'fecha'),
        Index('idx_registro_proyecto_fecha', 'proyecto_id', 'fecha'),
        Index('idx_registro_empleado_proyecto', 'empleado_id', 'proyecto_id'),
    )

    @property
    def es_hoy(self) -> bool:
        """Verifica si el registro es del día de hoy"""
        return self.fecha == date.today()

    @property
    def dias_desde_registro(self) -> int:
        """Calcula los días desde el registro"""
        return (date.today() - self.fecha).days

    @property
    def es_jornada_completa(self) -> bool:
        """Verifica si es una jornada completa (8 horas)"""
        return float(self.horas) >= 8.0

    @property
    def es_hora_extra(self) -> bool:
        """Verifica si hay horas extras (más de 8 horas)"""
        return float(self.horas) > 8.0

    @property
    def horas_extras(self) -> float:
        """Calcula las horas extras"""
        if self.es_hora_extra:
            return float(self.horas) - 8.0
        return 0.0

    def __repr__(self):
        return f"<RegistroHora {self.fecha} - {self.horas}h - Empleado {self.empleado_id}>"
