"""
Rutas de API para el módulo Costos.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.shared.storage import storage_service
from app.modules.costos.models import CategoriaGasto
from app.modules.costos.schemas import (
    CostoCreate,
    CostoUpdate,
    CostoResponse,
    CostoListResponse,
    CostoValidarRequest,
    CostoUploadFacturaResponse,
    EstadisticasCostos,
    CalcularManoObraRequest,
    CalcularManoObraResponse
)
from app.modules.costos.services import CostoService


router = APIRouter(prefix="/costos")


def get_costo_service(db: Session = Depends(get_db)) -> CostoService:
    """Dependency para obtener el servicio de costos"""
    return CostoService(db)


@router.get(
    "",
    response_model=CostoListResponse,
    summary="Listar costos/gastos",
    description="Obtiene una lista paginada de costos con filtros opcionales"
)
async def list_costos(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    proyecto_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    categoria: Optional[CategoriaGasto] = Query(None, description="Filtrar por categoría"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    validado: Optional[bool] = Query(None, description="Filtrar por validación"),
    con_factura: Optional[bool] = Query(None, description="Filtrar por presencia de factura"),
    search: Optional[str] = Query(None, description="Búsqueda en descripción y proveedor"),
    service: CostoService = Depends(get_costo_service)
):
    """
    Lista todos los costos con paginación y filtros opcionales.

    Filtros disponibles:
    - **proyecto_id**: Filtrar por proyecto específico
    - **categoria**: Filtrar por categoría de gasto
    - **fecha_desde/fecha_hasta**: Rango de fechas
    - **validado**: Solo gastos validados/no validados
    - **con_factura**: Solo gastos con/sin factura adjunta
    - **search**: Búsqueda en descripción y proveedor
    """
    skip = (page - 1) * page_size
    costos, total, total_monto = service.get_costos(
        skip=skip,
        limit=page_size,
        proyecto_id=proyecto_id,
        categoria=categoria,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        validado=validado,
        con_factura=con_factura,
        search=search
    )

    return CostoListResponse(
        total=total,
        total_monto=total_monto,
        items=costos,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{costo_id}",
    response_model=CostoResponse,
    summary="Obtener costo por ID",
    description="Obtiene los detalles completos de un costo"
)
async def get_costo(
    costo_id: str,
    service: CostoService = Depends(get_costo_service)
):
    """
    Obtiene un costo por su ID.

    - **costo_id**: ID único del costo (UUID)
    """
    return service.get_costo_by_id(costo_id)


@router.post(
    "",
    response_model=CostoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear costo/gasto",
    description="Registra un nuevo costo/gasto"
)
async def create_costo(
    costo_data: CostoCreate,
    service: CostoService = Depends(get_costo_service)
):
    """
    Crea un nuevo registro de costo/gasto.

    Validaciones:
    - El proyecto debe existir
    - El monto debe ser mayor a 0
    - La fecha no puede ser futura
    """
    return service.create_costo(costo_data)


@router.put(
    "/{costo_id}",
    response_model=CostoResponse,
    summary="Actualizar costo",
    description="Actualiza un costo existente"
)
async def update_costo(
    costo_id: str,
    costo_data: CostoUpdate,
    service: CostoService = Depends(get_costo_service)
):
    """
    Actualiza un costo existente.

    - **costo_id**: ID del costo a actualizar
    - Solo se actualizan los campos proporcionados
    """
    return service.update_costo(costo_id, costo_data)


@router.delete(
    "/{costo_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar costo",
    description="Elimina un costo"
)
async def delete_costo(
    costo_id: str,
    service: CostoService = Depends(get_costo_service)
):
    """
    Elimina un costo.

    - **costo_id**: ID del costo a eliminar
    """
    return service.delete_costo(costo_id)


@router.post(
    "/{costo_id}/factura",
    response_model=CostoUploadFacturaResponse,
    summary="Subir factura",
    description="Sube la foto o PDF de una factura"
)
async def upload_factura(
    costo_id: str,
    file: UploadFile = File(..., description="Archivo de la factura (JPG, PNG, PDF)"),
    service: CostoService = Depends(get_costo_service)
):
    """
    Sube una factura para un costo.

    - **costo_id**: ID del costo
    - **file**: Archivo de imagen o PDF (max 10MB)

    Tipos permitidos: JPG, PNG, PDF
    """
    return service.upload_factura(costo_id, file, storage_service)


@router.post(
    "/{costo_id}/validar",
    response_model=CostoResponse,
    summary="Validar/rechazar costo",
    description="Valida o rechaza un costo"
)
async def validar_costo(
    costo_id: str,
    validacion_data: CostoValidarRequest,
    service: CostoService = Depends(get_costo_service)
):
    """
    Valida o rechaza un costo.

    - **costo_id**: ID del costo
    - **validado**: True para validar, False para rechazar
    - **notas_validacion**: Notas opcionales sobre la validación
    """
    # TODO: Obtener usuario actual de la sesión cuando exista auth
    return service.validar_costo(costo_id, validacion_data)


@router.get(
    "/proyecto/{proyecto_id}/total",
    summary="Total gastado en proyecto",
    description="Obtiene el total gastado en un proyecto"
)
async def get_total_proyecto(
    proyecto_id: str,
    service: CostoService = Depends(get_costo_service)
):
    """
    Obtiene el resumen de gastos de un proyecto.

    Incluye:
    - Total gastado
    - Porcentaje del presupuesto
    - Balance restante
    - Alertas si está cerca del límite
    """
    return service.get_total_por_proyecto(proyecto_id)


@router.get(
    "/stats/general",
    response_model=EstadisticasCostos,
    summary="Estadísticas de costos",
    description="Obtiene estadísticas generales de costos"
)
async def get_estadisticas(
    periodo: str = Query("todos", description="Periodo: hoy, semana, mes, año, todos"),
    service: CostoService = Depends(get_costo_service)
):
    """
    Obtiene estadísticas de costos según periodo.

    Incluye:
    - Total de gastos
    - Total por categoría
    - Total por proyecto
    - Gastos sin validar
    - Gastos sin factura
    """
    return service.get_estadisticas(periodo)


@router.post(
    "/calcular-mano-obra",
    response_model=CalcularManoObraResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calcular costo de mano de obra",
    description="Calcula automáticamente el costo de mano de obra basado en registros de horas"
)
async def calcular_mano_obra(
    solicitud: CalcularManoObraRequest,
    service: CostoService = Depends(get_costo_service)
):
    """
    Calcula el costo de mano de obra para un proyecto en un periodo específico.

    Este endpoint:
    1. Obtiene todos los registros de horas del proyecto en el periodo especificado
    2. Calcula el costo por cada empleado (horas × tarifa_hora)
    3. Crea automáticamente un nuevo costo en la categoría MANO_OBRA
    4. Marca el costo como validado automáticamente

    Parámetros:
    - **proyecto_id**: ID del proyecto
    - **fecha_desde**: Fecha inicial del periodo
    - **fecha_hasta**: Fecha final del periodo
    - **descripcion**: Descripción personalizada (opcional, default: "Mano de obra del [periodo]")

    Retorna:
    - Detalle del costo creado
    - Monto total calculado
    - Desglose por empleado (horas, tarifa, costo)
    - ID del costo creado en la base de datos

    Nota: Solo se incluyen empleados que tengan tarifa_hora configurada.
    """
    return service.calcular_mano_obra(solicitud)
