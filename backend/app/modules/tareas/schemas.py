"""
Schemas de Tareas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TareaBase(BaseModel):
    """Schema base de Tarea"""
    titulo: str = Field(..., min_length=1, max_length=200, description="Título de la tarea")
    descripcion: Optional[str] = Field(None, description="Descripción detallada de la tarea")
    proyecto_id: str = Field(..., description="ID del proyecto al que pertenece")
    asignado_a_id: Optional[str] = Field(None, description="ID del usuario asignado (opcional)")
    estado: str = Field(default="pendiente", description="Estado de la tarea")
    prioridad: str = Field(default="media", description="Prioridad de la tarea")
    fecha_vencimiento: Optional[datetime] = Field(None, description="Fecha de vencimiento")
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha de inicio")

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        """Valida que el estado sea válido"""
        estados_validos = ['pendiente', 'en_progreso', 'completada', 'cancelada']
        v_lower = v.lower()
        if v_lower not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v_lower

    @field_validator('prioridad')
    @classmethod
    def validar_prioridad(cls, v: str) -> str:
        """Valida que la prioridad sea válida"""
        prioridades_validas = ['baja', 'media', 'alta', 'urgente']
        v_lower = v.lower()
        if v_lower not in prioridades_validas:
            raise ValueError(f'Prioridad debe ser una de: {", ".join(prioridades_validas)}')
        return v_lower


class TareaCreate(TareaBase):
    """Schema para crear una tarea"""
    pass


class TareaUpdate(BaseModel):
    """Schema para actualizar una tarea (todos los campos opcionales)"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    asignado_a_id: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    fecha_vencimiento: Optional[datetime] = None
    fecha_inicio: Optional[datetime] = None
    fecha_completada: Optional[datetime] = None

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el estado sea válido si se proporciona"""
        if v is None:
            return v
        estados_validos = ['pendiente', 'en_progreso', 'completada', 'cancelada']
        v_lower = v.lower()
        if v_lower not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v_lower

    @field_validator('prioridad')
    @classmethod
    def validar_prioridad(cls, v: Optional[str]) -> Optional[str]:
        """Valida que la prioridad sea válida si se proporciona"""
        if v is None:
            return v
        prioridades_validas = ['baja', 'media', 'alta', 'urgente']
        v_lower = v.lower()
        if v_lower not in prioridades_validas:
            raise ValueError(f'Prioridad debe ser una de: {", ".join(prioridades_validas)}')
        return v_lower


class CambiarEstadoTarea(BaseModel):
    """Schema para cambiar el estado de una tarea"""
    estado: str = Field(..., description="Nuevo estado")

    @field_validator('estado')
    @classmethod
    def validar_estado(cls, v: str) -> str:
        """Valida que el estado sea válido"""
        estados_validos = ['pendiente', 'en_progreso', 'completada', 'cancelada']
        v_lower = v.lower()
        if v_lower not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v_lower


class TareaResponse(TareaBase):
    """Schema de respuesta de Tarea"""
    id: str
    creado_por_id: str
    fecha_completada: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime

    # Campos calculados
    esta_vencida: Optional[bool] = None
    dias_hasta_vencimiento: Optional[int] = None
    esta_completada: Optional[bool] = None
    duracion_dias: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "titulo": "Instalación de cañerías",
                "descripcion": "Instalar todo el sistema de cañerías del primer piso",
                "proyecto_id": "proj-001",
                "asignado_a_id": "user-001",
                "creado_por_id": "user-admin",
                "estado": "en_progreso",
                "prioridad": "alta",
                "fecha_vencimiento": "2025-11-15T00:00:00",
                "fecha_inicio": "2025-11-01T00:00:00",
                "esta_vencida": False,
                "dias_hasta_vencimiento": 8,
                "esta_completada": False,
                "duracion_dias": 6,
                "creado_en": "2025-11-01T10:00:00",
                "actualizado_en": "2025-11-07T14:30:00"
            }
        }
    }


class TareaListResponse(BaseModel):
    """Schema para lista paginada de tareas"""
    total: int = Field(..., description="Total de tareas")
    items: list[TareaResponse] = Field(..., description="Lista de tareas")
    page: int = Field(1, ge=1, description="Página actual")
    page_size: int = Field(50, ge=1, le=100, description="Tamaño de página")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 42,
                "items": [],
                "page": 1,
                "page_size": 50
            }
        }
    }


class TareaStatsResponse(BaseModel):
    """Schema para estadísticas de tareas"""
    total_tareas: int = Field(..., description="Total de tareas")
    por_estado: dict[str, int] = Field(..., description="Cantidad por estado")
    por_prioridad: dict[str, int] = Field(..., description="Cantidad por prioridad")
    tareas_vencidas: int = Field(..., description="Tareas vencidas")
    tareas_hoy: int = Field(..., description="Tareas que vencen hoy")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_tareas": 42,
                "por_estado": {
                    "pendiente": 15,
                    "en_progreso": 12,
                    "completada": 10,
                    "cancelada": 5
                },
                "por_prioridad": {
                    "baja": 10,
                    "media": 20,
                    "alta": 8,
                    "urgente": 4
                },
                "tareas_vencidas": 3,
                "tareas_hoy": 5
            }
        }
    }
