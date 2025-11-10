"""
Schemas de Personal
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, EmailStr


class EmpleadoBase(BaseModel):
    """Schema base de Empleado"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del empleado")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido del empleado")
    documento_identidad: Optional[str] = Field(None, max_length=50, description="Documento de identidad")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    email: Optional[EmailStr] = Field(None, description="Email del empleado")
    cargo: str = Field(..., min_length=1, max_length=50, description="Cargo del empleado")
    tarifa_hora: Decimal = Field(..., ge=0, description="Tarifa por hora en moneda local")
    fecha_ingreso: Optional[datetime] = Field(None, description="Fecha de ingreso")
    activo: bool = Field(default=True, description="Si el empleado está activo")
    notas: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    @field_validator('tarifa_hora')
    @classmethod
    def validar_tarifa(cls, v: Decimal) -> Decimal:
        """Valida que la tarifa sea positiva"""
        if v < 0:
            raise ValueError('La tarifa por hora debe ser positiva')
        return v

    @field_validator('cargo')
    @classmethod
    def normalizar_cargo(cls, v: str) -> str:
        """Normaliza el cargo a minúsculas"""
        return v.lower().strip()


class EmpleadoCreate(EmpleadoBase):
    """Schema para crear un empleado"""
    usuario_id: Optional[str] = Field(None, description="ID del usuario asociado (opcional)")


class EmpleadoUpdate(BaseModel):
    """Schema para actualizar un empleado (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    documento_identidad: Optional[str] = Field(None, max_length=50)
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    cargo: Optional[str] = Field(None, min_length=1, max_length=50)
    tarifa_hora: Optional[Decimal] = Field(None, ge=0)
    fecha_ingreso: Optional[datetime] = None
    fecha_salida: Optional[datetime] = None
    activo: Optional[bool] = None
    notas: Optional[str] = Field(None, max_length=500)
    usuario_id: Optional[str] = None

    @field_validator('tarifa_hora')
    @classmethod
    def validar_tarifa(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Valida que la tarifa sea positiva si se proporciona"""
        if v is not None and v < 0:
            raise ValueError('La tarifa por hora debe ser positiva')
        return v

    @field_validator('cargo')
    @classmethod
    def normalizar_cargo(cls, v: Optional[str]) -> Optional[str]:
        """Normaliza el cargo a minúsculas si se proporciona"""
        return v.lower().strip() if v else None


class EmpleadoResponse(EmpleadoBase):
    """Schema de respuesta de Empleado"""
    id: str
    usuario_id: Optional[str]
    fecha_salida: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: datetime

    # Campos calculados
    nombre_completo: Optional[str] = None
    dias_antiguedad: Optional[int] = None
    esta_activo: Optional[bool] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Juan",
                "apellido": "Pérez",
                "documento_identidad": "12345678",
                "telefono": "+54911234567",
                "email": "juan.perez@example.com",
                "cargo": "oficial",
                "tarifa_hora": 1500.00,
                "fecha_ingreso": "2024-01-15T00:00:00",
                "activo": True,
                "notas": "Especialista en albañilería",
                "nombre_completo": "Juan Pérez",
                "dias_antiguedad": 295,
                "esta_activo": True,
                "creado_en": "2024-01-15T10:30:00",
                "actualizado_en": "2024-01-15T10:30:00"
            }
        }
    }


class EmpleadoListResponse(BaseModel):
    """Schema para lista paginada de empleados"""
    total: int = Field(..., description="Total de empleados")
    items: list[EmpleadoResponse] = Field(..., description="Lista de empleados")
    page: int = Field(1, ge=1, description="Página actual")
    page_size: int = Field(50, ge=1, le=100, description="Tamaño de página")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 25,
                "items": [],
                "page": 1,
                "page_size": 50
            }
        }
    }


class EmpleadoStatsResponse(BaseModel):
    """Schema para estadísticas de empleados"""
    total_empleados: int = Field(..., description="Total de empleados")
    empleados_activos: int = Field(..., description="Empleados activos")
    empleados_inactivos: int = Field(..., description="Empleados inactivos")
    por_cargo: dict[str, int] = Field(..., description="Cantidad por cargo")
    tarifa_promedio: Decimal = Field(..., description="Tarifa promedio por hora")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_empleados": 25,
                "empleados_activos": 20,
                "empleados_inactivos": 5,
                "por_cargo": {
                    "obrero": 10,
                    "oficial": 8,
                    "maestro_obra": 2
                },
                "tarifa_promedio": 1250.50
            }
        }
    }
