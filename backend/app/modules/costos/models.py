"""
Modelos de base de datos para el módulo de Costos/Gastos.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Numeric, Enum, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CategoriaGasto(str, PyEnum):
    """Categorías de gastos en un proyecto"""
    MATERIALES = "materiales"
    MANO_OBRA = "mano_obra"
    TRANSPORTE = "transporte"
    HERRAMIENTAS = "herramientas"
    SUBCONTRATO = "subcontrato"
    PERMISOS = "permisos"
    SERVICIOS = "servicios"
    OTROS = "otros"


class MetodoCaptura(str, PyEnum):
    """Método usado para capturar el gasto"""
    MANUAL_WEB = "manual_web"
    MANUAL_BOT = "manual_bot"
    FOTO_BOT = "foto_bot"
    OCR_AUTO = "ocr_auto"
    VOZ = "voz"
    API = "api"


class Costo(Base):
    """
    Modelo de Costo/Gasto de un proyecto.

    Representa un gasto individual asociado a un proyecto,
    con foto de factura opcional y validación.
    """
    __tablename__ = "costos"

    # Identificadores
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Relaciones
    proyecto_id = Column(String(36), ForeignKey("proyectos.id"), nullable=False, index=True)
    # personal_id = Column(String(36), ForeignKey("personal.id"), nullable=True)  # Fase 2
    # proveedor_id = Column(String(36), ForeignKey("proveedores.id"), nullable=True)  # Fase 2

    # Información del gasto
    categoria = Column(Enum(CategoriaGasto), nullable=False, index=True)
    monto = Column(Numeric(precision=12, scale=2), nullable=False)
    descripcion = Column(Text, nullable=False)

    # Proveedor (temporalmente como string, luego será FK)
    proveedor_nombre = Column(String(200), nullable=True)

    # Archivo adjunto (factura)
    factura_url = Column(String(500), nullable=True)
    factura_filename = Column(String(200), nullable=True)

    # Metadata de la captura
    fecha_gasto = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    metodo_captura = Column(Enum(MetodoCaptura), default=MetodoCaptura.MANUAL_WEB, nullable=False)

    # Validación
    validado = Column(Boolean, default=False, nullable=False)
    validado_por = Column(String(36), nullable=True)  # FK a usuarios cuando exista
    validado_en = Column(DateTime, nullable=True)
    notas_validacion = Column(Text, nullable=True)

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    proyecto = relationship("Proyecto", foreign_keys=[proyecto_id])
    # personal = relationship("Personal", foreign_keys=[personal_id])  # Fase 2

    def __repr__(self):
        return f"<Costo(id='{self.id}', monto={self.monto}, categoria='{self.categoria}')>"

    @property
    def dias_desde_gasto(self) -> int:
        """Calcula los días transcurridos desde el gasto"""
        return (datetime.utcnow() - self.fecha_gasto).days

    @property
    def tiene_factura(self) -> bool:
        """Indica si tiene factura adjunta"""
        return bool(self.factura_url)
