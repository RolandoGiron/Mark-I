"""
Modelos de Personal
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class CargoEmpleado(str, PyEnum):
    """Tipos de cargo para empleados"""
    OBRERO = "obrero"
    OFICIAL = "oficial"
    MAESTRO_OBRA = "maestro_obra"
    SUPERVISOR = "supervisor"
    INGENIERO = "ingeniero"
    ADMINISTRATIVO = "administrativo"


class Empleado(Base):
    """Modelo de Empleado/Personal"""
    __tablename__ = "empleados"

    # Identificadores
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.id"), nullable=True, index=True)

    # Datos personales
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    documento_identidad = Column(String(50), nullable=True, unique=True, index=True)
    telefono = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    # Datos laborales
    cargo = Column(String(50), nullable=False, index=True)  # Usamos String para flexibilidad
    tarifa_hora = Column(Numeric(precision=10, scale=2), nullable=False, default=0)
    fecha_ingreso = Column(DateTime, nullable=True)
    fecha_salida = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True, nullable=False, index=True)

    # Notas adicionales
    notas = Column(String(500), nullable=True)

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id], backref="empleado_asociado")

    # Índices compuestos
    __table_args__ = (
        Index('idx_empleado_nombre_completo', 'nombre', 'apellido'),
        Index('idx_empleado_activo_cargo', 'activo', 'cargo'),
    )

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del empleado"""
        return f"{self.nombre} {self.apellido}"

    @property
    def dias_antiguedad(self) -> int:
        """Calcula los días de antigüedad del empleado"""
        if not self.fecha_ingreso:
            return 0
        fecha_fin = self.fecha_salida if self.fecha_salida else datetime.utcnow()
        return (fecha_fin - self.fecha_ingreso).days

    @property
    def esta_activo(self) -> bool:
        """Verifica si el empleado está activo"""
        return self.activo and (self.fecha_salida is None or self.fecha_salida > datetime.utcnow())

    def __repr__(self):
        return f"<Empleado {self.nombre_completo} - {self.cargo}>"
