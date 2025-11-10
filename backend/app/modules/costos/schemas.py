"""
Schemas de Pydantic para validación de datos del módulo Costos.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.modules.costos.models import CategoriaGasto, MetodoCaptura


class CostoBase(BaseModel):
    """Schema base con campos comunes"""
    proyecto_id: str = Field(..., description="ID del proyecto asociado")
    categoria: CategoriaGasto = Field(..., description="Categoría del gasto")
    monto: Decimal = Field(..., gt=0, description="Monto del gasto")
    descripcion: str = Field(..., min_length=1, description="Descripción del gasto")
    proveedor_nombre: Optional[str] = Field(None, max_length=200, description="Nombre del proveedor")
    fecha_gasto: datetime = Field(default_factory=datetime.utcnow, description="Fecha del gasto")

    @field_validator('monto')
    @classmethod
    def validar_monto(cls, v: Decimal) -> Decimal:
        """Valida que el monto sea positivo"""
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        if v > Decimal("10000000"):  # 10M límite razonable
            raise ValueError('El monto parece excesivo. Verifica el monto.')
        return v


class CostoCreate(CostoBase):
    """Schema para crear un costo"""
    metodo_captura: MetodoCaptura = Field(default=MetodoCaptura.MANUAL_WEB, description="Método de captura")


class CostoUpdate(BaseModel):
    """Schema para actualizar un costo (todos los campos opcionales)"""
    categoria: Optional[CategoriaGasto] = None
    monto: Optional[Decimal] = Field(None, gt=0)
    descripcion: Optional[str] = Field(None, min_length=1)
    proveedor_nombre: Optional[str] = Field(None, max_length=200)
    fecha_gasto: Optional[datetime] = None
    validado: Optional[bool] = None
    notas_validacion: Optional[str] = None


class CostoResponse(CostoBase):
    """Schema de respuesta de un costo"""
    id: str
    factura_url: Optional[str] = None
    factura_filename: Optional[str] = None
    metodo_captura: MetodoCaptura
    validado: bool
    validado_por: Optional[str] = None
    validado_en: Optional[datetime] = None
    notas_validacion: Optional[str] = None
    creado_en: datetime
    actualizado_en: datetime
    dias_desde_gasto: int
    tiene_factura: bool

    # Datos del proyecto (nested)
    proyecto_codigo: Optional[str] = None
    proyecto_nombre: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "proyecto_id": "987fcdeb-51a2-43d8-9876-543210fedcba",
                "proyecto_codigo": "CASA-001",
                "proyecto_nombre": "Casa Martinez #23",
                "categoria": "materiales",
                "monto": 1250.50,
                "descripcion": "Cemento y arena para cimientos",
                "proveedor_nombre": "Home Depot",
                "fecha_gasto": "2025-11-04T10:30:00",
                "factura_url": "/uploads/facturas/factura-123.jpg",
                "factura_filename": "factura-123.jpg",
                "metodo_captura": "foto_bot",
                "validado": True,
                "validado_por": "admin-user-id",
                "validado_en": "2025-11-04T11:00:00",
                "notas_validacion": "Factura verificada",
                "creado_en": "2025-11-04T10:30:00",
                "actualizado_en": "2025-11-04T11:00:00",
                "dias_desde_gasto": 0,
                "tiene_factura": True
            }
        }
    }


class CostoListResponse(BaseModel):
    """Schema para lista paginada de costos"""
    total: int
    total_monto: Decimal = Field(description="Suma total de los montos")
    items: list[CostoResponse]
    page: int = 1
    page_size: int = 50


class CostoUploadFacturaResponse(BaseModel):
    """Schema de respuesta al subir una factura"""
    id: str
    factura_url: str
    factura_filename: str
    message: str = "Factura subida exitosamente"


class CostoValidarRequest(BaseModel):
    """Schema para validar un costo"""
    validado: bool = Field(..., description="Estado de validación")
    notas_validacion: Optional[str] = Field(None, description="Notas sobre la validación")


class EstadisticasCostos(BaseModel):
    """Schema para estadísticas de costos"""
    total_gastos: Decimal
    total_por_categoria: dict[str, Decimal]
    total_por_proyecto: dict[str, Decimal]
    gastos_sin_validar: int
    gastos_sin_factura: int
    periodo: str = "todos"  # puede ser: "hoy", "semana", "mes", "año", "todos"

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_gastos": 125000.50,
                "total_por_categoria": {
                    "materiales": 75000.00,
                    "mano_obra": 35000.50,
                    "transporte": 15000.00
                },
                "total_por_proyecto": {
                    "CASA-001": 85000.00,
                    "LOCAL-002": 40000.50
                },
                "gastos_sin_validar": 5,
                "gastos_sin_factura": 3,
                "periodo": "mes"
            }
        }
    }


class CalcularManoObraRequest(BaseModel):
    """Schema para solicitar el cálculo de costos de mano de obra"""
    proyecto_id: str = Field(..., description="ID del proyecto")
    fecha_desde: datetime = Field(..., description="Fecha inicial del periodo")
    fecha_hasta: datetime = Field(..., description="Fecha final del periodo")
    descripcion: Optional[str] = Field(
        None,
        description="Descripción personalizada (default: 'Mano de obra del [periodo]')"
    )


class ManoObraCalculoDetalle(BaseModel):
    """Detalle de cálculo de mano de obra por empleado"""
    empleado_id: str
    empleado_nombre: str
    total_horas: Decimal
    tarifa_hora: Decimal
    costo_total: Decimal


class CalcularManoObraResponse(BaseModel):
    """Schema de respuesta del cálculo de mano de obra"""
    costo_id: str = Field(..., description="ID del costo creado")
    proyecto_id: str
    proyecto_nombre: str
    periodo_inicio: datetime
    periodo_fin: datetime
    total_horas: Decimal
    monto_total: Decimal
    cantidad_empleados: int
    detalle_empleados: list[ManoObraCalculoDetalle]
    mensaje: str = "Costo de mano de obra calculado y registrado exitosamente"

    model_config = {
        "json_schema_extra": {
            "example": {
                "costo_id": "123e4567-e89b-12d3-a456-426614174000",
                "proyecto_id": "proj-001",
                "proyecto_nombre": "Edificio Central",
                "periodo_inicio": "2025-11-01T00:00:00",
                "periodo_fin": "2025-11-30T23:59:59",
                "total_horas": 168.5,
                "monto_total": 252750.00,
                "cantidad_empleados": 3,
                "detalle_empleados": [
                    {
                        "empleado_id": "emp-001",
                        "empleado_nombre": "Juan Pérez",
                        "total_horas": 85.0,
                        "tarifa_hora": 1500.00,
                        "costo_total": 127500.00
                    }
                ],
                "mensaje": "Costo de mano de obra calculado y registrado exitosamente"
            }
        }
    }
