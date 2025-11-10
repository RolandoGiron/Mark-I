"""
Modelos de Notificaciones
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Index, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class TipoNotificacion(str, PyEnum):
    """Tipos de notificación"""
    ALERTA_PRESUPUESTO = "alerta_presupuesto"  # Presupuesto cerca del límite
    TAREA_ASIGNADA = "tarea_asignada"  # Nueva tarea asignada
    TAREA_VENCIDA = "tarea_vencida"  # Tarea vencida
    GASTO_PENDIENTE = "gasto_pendiente"  # Gasto pendiente de validación
    PROYECTO_INICIADO = "proyecto_iniciado"  # Proyecto iniciado
    PROYECTO_COMPLETADO = "proyecto_completado"  # Proyecto completado
    HORAS_REGISTRADAS = "horas_registradas"  # Horas registradas
    MANO_OBRA_CALCULADA = "mano_obra_calculada"  # Costo de MO calculado


class Notificacion(Base):
    """Modelo de Notificación"""
    __tablename__ = "notificaciones"

    # Identificadores
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String(36), ForeignKey("usuarios.id"), nullable=False, index=True)

    # Información de la notificación
    tipo = Column(String(50), nullable=False, index=True)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    leida = Column(Boolean, default=False, nullable=False, index=True)

    # Datos adicionales (JSON flexible para diferentes tipos)
    datos = Column(JSON, nullable=True)  # Puede contener IDs de proyecto, tarea, costo, etc.

    # Timestamps
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    leida_en = Column(DateTime, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id], backref="notificaciones")

    # Índices compuestos
    __table_args__ = (
        Index('idx_notif_usuario_leida', 'usuario_id', 'leida'),
        Index('idx_notif_usuario_tipo', 'usuario_id', 'tipo'),
        Index('idx_notif_creado', 'creado_en'),
    )

    @property
    def esta_leida(self) -> bool:
        """Verifica si la notificación está leída"""
        return self.leida

    @property
    def es_reciente(self) -> bool:
        """Verifica si la notificación fue creada en las últimas 24 horas"""
        return (datetime.utcnow() - self.creado_en).total_seconds() < 86400

    @property
    def tiempo_transcurrido_str(self) -> str:
        """Retorna una cadena legible del tiempo transcurrido"""
        delta = datetime.utcnow() - self.creado_en

        if delta.total_seconds() < 60:
            return "Hace menos de 1 minuto"
        elif delta.total_seconds() < 3600:
            minutos = int(delta.total_seconds() / 60)
            return f"Hace {minutos} minuto{'s' if minutos != 1 else ''}"
        elif delta.total_seconds() < 86400:
            horas = int(delta.total_seconds() / 3600)
            return f"Hace {horas} hora{'s' if horas != 1 else ''}"
        else:
            dias = delta.days
            return f"Hace {dias} día{'s' if dias != 1 else ''}"

    def __repr__(self):
        return f"<Notificacion {self.tipo} - {self.titulo} - {'Leída' if self.leida else 'No leída'}>"
