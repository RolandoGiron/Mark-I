"""
Schemas de Pydantic para validación de datos del módulo Proyectos.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

from app.modules.proyectos.models import EstadoProyecto


class ProyectoBase(BaseModel):
    """Schema base con campos comunes"""
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único del proyecto")
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del proyecto")
    cliente: str = Field(..., min_length=1, max_length=200, description="Nombre del cliente")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del proyecto")
    presupuesto_total: Decimal = Field(..., gt=0, description="Presupuesto total del proyecto")
    horas_presupuestadas: Optional[Decimal] = Field(None, ge=0, description="Horas estimadas del proyecto")
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha de inicio del proyecto")
    fecha_fin_estimada: Optional[datetime] = Field(None, description="Fecha estimada de finalización")
    estado: EstadoProyecto = Field(default=EstadoProyecto.PROSPECTO, description="Estado actual del proyecto")
    datos_adicionales: Optional[Dict[str, Any]] = Field(None, description="Metadata adicional en formato JSON")

    @field_validator('presupuesto_total')
    @classmethod
    def validar_presupuesto(cls, v: Decimal) -> Decimal:
        """Valida que el presupuesto sea positivo"""
        if v <= 0:
            raise ValueError('El presupuesto debe ser mayor a 0')
        return v

    @field_validator('fecha_fin_estimada')
    @classmethod
    def validar_fechas(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Valida que la fecha de fin sea posterior a la de inicio"""
        if v and info.data.get('fecha_inicio'):
            if v < info.data['fecha_inicio']:
                raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class ProyectoCreate(ProyectoBase):
    """Schema para crear un proyecto"""
    pass


class ProyectoUpdate(BaseModel):
    """Schema para actualizar un proyecto (todos los campos opcionales)"""
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    cliente: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    presupuesto_total: Optional[Decimal] = Field(None, gt=0)
    horas_presupuestadas: Optional[Decimal] = Field(None, ge=0)
    fecha_inicio: Optional[datetime] = None
    fecha_fin_estimada: Optional[datetime] = None
    fecha_fin_real: Optional[datetime] = None
    estado: Optional[EstadoProyecto] = None
    datos_adicionales: Optional[Dict[str, Any]] = None


class ProyectoResponse(ProyectoBase):
    """Schema de respuesta de un proyecto"""
    id: str
    fecha_fin_real: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime
    dias_transcurridos: Optional[int] = None
    dias_restantes: Optional[int] = None

    model_config = {
        "from_attributes": True,  # Permite crear desde modelos SQLAlchemy
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "codigo": "CASA-001",
                "nombre": "Casa Martinez #23",
                "cliente": "Juan Martinez",
                "descripcion": "Construcción de casa residencial de 2 pisos",
                "presupuesto_total": 500000.00,
                "horas_presupuestadas": 200.0,
                "fecha_inicio": "2025-11-01T00:00:00",
                "fecha_fin_estimada": "2026-03-01T00:00:00",
                "fecha_fin_real": None,
                "estado": "en_progreso",
                "datos_adicionales": {"ubicacion": "Zona Norte", "tipo": "Residencial"},
                "creado_en": "2025-11-04T10:00:00",
                "actualizado_en": "2025-11-04T10:00:00",
                "dias_transcurridos": 3,
                "dias_restantes": 117
            }
        }
    }


class ProyectoResumen(BaseModel):
    """Schema para resumen financiero de un proyecto"""
    id: str
    codigo: str
    nombre: str
    presupuesto_total: Decimal
    total_gastado: Decimal = Field(default=0, description="Total gastado hasta ahora")
    porcentaje_gastado: Decimal = Field(default=0, description="Porcentaje del presupuesto gastado")
    balance: Decimal = Field(default=0, description="Balance restante")
    estado: EstadoProyecto
    en_alerta: bool = Field(default=False, description="Si el gasto supera el 90% del presupuesto")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "codigo": "CASA-001",
                "nombre": "Casa Martinez #23",
                "presupuesto_total": 500000.00,
                "total_gastado": 320000.00,
                "porcentaje_gastado": 64.0,
                "balance": 180000.00,
                "estado": "en_progreso",
                "en_alerta": False
            }
        }
    }


class ProyectoListResponse(BaseModel):
    """Schema para lista paginada de proyectos"""
    total: int
    items: list[ProyectoResponse]
    page: int = 1
    page_size: int = 50
