"""
Schemas de Horas
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RegistroHoraBase(BaseModel):
    """Schema base de Registro de Hora"""
    empleado_id: str = Field(..., description="ID del empleado")
    proyecto_id: str = Field(..., description="ID del proyecto")
    tarea_id: Optional[str] = Field(None, description="ID de la tarea (opcional)")
    fecha: date = Field(..., description="Fecha del registro")
    horas: Decimal = Field(..., ge=0.5, le=24, description="Cantidad de horas trabajadas")
    descripcion: Optional[str] = Field(None, description="Descripción del trabajo realizado")

    @field_validator('horas')
    @classmethod
    def validar_horas(cls, v: Decimal) -> Decimal:
        """Valida que las horas sean válidas"""
        if v < Decimal('0.5'):
            raise ValueError('Las horas deben ser al menos 0.5')
        if v > Decimal('24'):
            raise ValueError('Las horas no pueden exceder 24 por día')
        return v

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v: date) -> date:
        """Valida que la fecha no sea futura"""
        if v > date.today():
            raise ValueError('No se pueden registrar horas para fechas futuras')
        return v


class RegistroHoraCreate(RegistroHoraBase):
    """Schema para crear un registro de horas"""
    pass


class RegistroHoraUpdate(BaseModel):
    """Schema para actualizar un registro de horas (todos los campos opcionales)"""
    tarea_id: Optional[str] = None
    fecha: Optional[date] = None
    horas: Optional[Decimal] = Field(None, ge=0.5, le=24)
    descripcion: Optional[str] = None

    @field_validator('horas')
    @classmethod
    def validar_horas(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Valida que las horas sean válidas si se proporcionan"""
        if v is not None:
            if v < Decimal('0.5'):
                raise ValueError('Las horas deben ser al menos 0.5')
            if v > Decimal('24'):
                raise ValueError('Las horas no pueden exceder 24 por día')
        return v

    @field_validator('fecha')
    @classmethod
    def validar_fecha(cls, v: Optional[date]) -> Optional[date]:
        """Valida que la fecha no sea futura si se proporciona"""
        if v is not None and v > date.today():
            raise ValueError('No se pueden registrar horas para fechas futuras')
        return v


class RegistroHoraResponse(RegistroHoraBase):
    """Schema de respuesta de Registro de Hora"""
    id: str
    creado_en: datetime
    actualizado_en: datetime

    # Campos calculados
    es_hoy: Optional[bool] = None
    dias_desde_registro: Optional[int] = None
    es_jornada_completa: Optional[bool] = None
    es_hora_extra: Optional[bool] = None
    horas_extras: Optional[float] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "empleado_id": "emp-001",
                "proyecto_id": "proj-001",
                "tarea_id": "tarea-001",
                "fecha": "2025-11-07",
                "horas": 8.5,
                "descripcion": "Instalación de cañerías en el primer piso",
                "es_hoy": True,
                "dias_desde_registro": 0,
                "es_jornada_completa": True,
                "es_hora_extra": True,
                "horas_extras": 0.5,
                "creado_en": "2025-11-07T14:00:00",
                "actualizado_en": "2025-11-07T14:00:00"
            }
        }
    }


class RegistroHoraListResponse(BaseModel):
    """Schema para lista paginada de registros de horas"""
    total: int = Field(..., description="Total de registros")
    items: list[RegistroHoraResponse] = Field(..., description="Lista de registros")
    page: int = Field(1, ge=1, description="Página actual")
    page_size: int = Field(50, ge=1, le=100, description="Tamaño de página")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 150,
                "items": [],
                "page": 1,
                "page_size": 50
            }
        }
    }


class RegistroHoraStatsResponse(BaseModel):
    """Schema para estadísticas de horas"""
    total_registros: int = Field(..., description="Total de registros")
    total_horas: Decimal = Field(..., description="Total de horas trabajadas")
    total_horas_extras: Decimal = Field(..., description="Total de horas extras")
    promedio_horas_dia: Decimal = Field(..., description="Promedio de horas por día")
    dias_trabajados: int = Field(..., description="Cantidad de días con registro")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_registros": 150,
                "total_horas": 1200.5,
                "total_horas_extras": 45.5,
                "promedio_horas_dia": 8.0,
                "dias_trabajados": 150
            }
        }
    }


class ResumenHorasEmpleado(BaseModel):
    """Schema para resumen de horas por empleado"""
    empleado_id: str
    empleado_nombre: str
    total_horas: Decimal
    total_horas_extras: Decimal
    dias_trabajados: int
    tarifa_hora: Optional[Decimal] = None
    costo_total: Optional[Decimal] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "empleado_id": "emp-001",
                "empleado_nombre": "Juan Pérez",
                "total_horas": 168.5,
                "total_horas_extras": 12.5,
                "dias_trabajados": 21,
                "tarifa_hora": 1500.00,
                "costo_total": 252750.00
            }
        }
    }


class ResumenHorasProyecto(BaseModel):
    """Schema para resumen de horas por proyecto"""
    proyecto_id: str
    proyecto_nombre: str
    total_horas: Decimal
    total_horas_extras: Decimal
    cantidad_empleados: int
    costo_mano_obra: Optional[Decimal] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "proyecto_id": "proj-001",
                "proyecto_nombre": "Edificio Central",
                "total_horas": 500.0,
                "total_horas_extras": 35.0,
                "cantidad_empleados": 8,
                "costo_mano_obra": 750000.00
            }
        }
    }
