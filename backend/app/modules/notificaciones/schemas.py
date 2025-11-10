"""
Schemas de Notificaciones
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class NotificacionBase(BaseModel):
    """Schema base de Notificación"""
    tipo: str = Field(..., description="Tipo de notificación")
    titulo: str = Field(..., min_length=1, max_length=200, description="Título de la notificación")
    mensaje: str = Field(..., min_length=1, description="Mensaje de la notificación")
    datos: Optional[dict] = Field(None, description="Datos adicionales en formato JSON")


class NotificacionCreate(NotificacionBase):
    """Schema para crear una notificación"""
    usuario_id: str = Field(..., description="ID del usuario destinatario")


class NotificacionUpdate(BaseModel):
    """Schema para actualizar una notificación"""
    leida: bool = Field(..., description="Marcar como leída o no leída")


class NotificacionResponse(NotificacionBase):
    """Schema de respuesta de Notificación"""
    id: str
    usuario_id: str
    leida: bool
    creado_en: datetime
    leida_en: Optional[datetime] = None

    # Campos calculados
    esta_leida: Optional[bool] = None
    es_reciente: Optional[bool] = None
    tiempo_transcurrido_str: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "usuario_id": "user-001",
                "tipo": "tarea_asignada",
                "titulo": "Nueva tarea asignada",
                "mensaje": "Te han asignado la tarea 'Instalación de cañerías' en el proyecto Edificio Central",
                "leida": False,
                "datos": {
                    "tarea_id": "tarea-001",
                    "proyecto_id": "proj-001"
                },
                "creado_en": "2025-11-07T14:30:00",
                "leida_en": None,
                "esta_leida": False,
                "es_reciente": True,
                "tiempo_transcurrido_str": "Hace 5 minutos"
            }
        }
    }


class NotificacionListResponse(BaseModel):
    """Schema para lista paginada de notificaciones"""
    total: int = Field(..., description="Total de notificaciones")
    no_leidas: int = Field(..., description="Cantidad de notificaciones no leídas")
    items: list[NotificacionResponse] = Field(..., description="Lista de notificaciones")
    page: int = Field(1, ge=1, description="Página actual")
    page_size: int = Field(50, ge=1, le=100, description="Tamaño de página")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 25,
                "no_leidas": 5,
                "items": [],
                "page": 1,
                "page_size": 50
            }
        }
    }


class NotificacionStatsResponse(BaseModel):
    """Schema para estadísticas de notificaciones"""
    total_notificaciones: int = Field(..., description="Total de notificaciones")
    no_leidas: int = Field(..., description="Notificaciones no leídas")
    leidas: int = Field(..., description="Notificaciones leídas")
    por_tipo: dict[str, int] = Field(..., description="Cantidad por tipo")
    recientes_24h: int = Field(..., description="Notificaciones de las últimas 24 horas")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_notificaciones": 25,
                "no_leidas": 5,
                "leidas": 20,
                "por_tipo": {
                    "tarea_asignada": 10,
                    "alerta_presupuesto": 5,
                    "tarea_vencida": 10
                },
                "recientes_24h": 8
            }
        }
    }
