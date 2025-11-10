"""
Rutas de API para el módulo Proyectos.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.proyectos.models import EstadoProyecto
from app.modules.proyectos.schemas import (
    ProyectoCreate,
    ProyectoUpdate,
    ProyectoResponse,
    ProyectoListResponse,
    ProyectoResumen
)
from app.modules.proyectos.services import ProyectoService


router = APIRouter(prefix="/proyectos")


def get_proyecto_service(db: Session = Depends(get_db)) -> ProyectoService:
    """Dependency para obtener el servicio de proyectos"""
    return ProyectoService(db)


@router.get(
    "",
    response_model=ProyectoListResponse,
    summary="Listar proyectos",
    description="Obtiene una lista paginada de proyectos con filtros opcionales"
)
async def list_proyectos(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    estado: Optional[EstadoProyecto] = Query(None, description="Filtrar por estado"),
    cliente: Optional[str] = Query(None, description="Filtrar por nombre de cliente"),
    search: Optional[str] = Query(None, description="Búsqueda en código, nombre, cliente o descripción"),
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Lista todos los proyectos con paginación y filtros opcionales.

    - **page**: Número de página (default: 1)
    - **page_size**: Elementos por página (default: 50, max: 100)
    - **estado**: Filtrar por estado del proyecto
    - **cliente**: Filtrar por nombre de cliente (búsqueda parcial)
    - **search**: Búsqueda en múltiples campos
    """
    skip = (page - 1) * page_size
    proyectos, total = service.get_proyectos(
        skip=skip,
        limit=page_size,
        estado=estado,
        cliente=cliente,
        search=search
    )

    return ProyectoListResponse(
        total=total,
        items=proyectos,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{proyecto_id}",
    response_model=ProyectoResponse,
    summary="Obtener proyecto por ID",
    description="Obtiene los detalles completos de un proyecto"
)
async def get_proyecto(
    proyecto_id: str,
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Obtiene un proyecto por su ID.

    - **proyecto_id**: ID único del proyecto (UUID)
    """
    return service.get_proyecto_by_id(proyecto_id)


@router.get(
    "/codigo/{codigo}",
    response_model=ProyectoResponse,
    summary="Obtener proyecto por código",
    description="Obtiene los detalles de un proyecto por su código"
)
async def get_proyecto_by_codigo(
    codigo: str,
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Obtiene un proyecto por su código único.

    - **codigo**: Código del proyecto (ej: CASA-001)
    """
    return service.get_proyecto_by_codigo(codigo)


@router.post(
    "",
    response_model=ProyectoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear proyecto",
    description="Crea un nuevo proyecto"
)
async def create_proyecto(
    proyecto_data: ProyectoCreate,
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Crea un nuevo proyecto.

    Validaciones:
    - El código debe ser único
    - El presupuesto debe ser mayor a 0
    - Si se especifica fecha_fin_estimada, debe ser posterior a fecha_inicio
    """
    return service.create_proyecto(proyecto_data)


@router.put(
    "/{proyecto_id}",
    response_model=ProyectoResponse,
    summary="Actualizar proyecto",
    description="Actualiza un proyecto existente"
)
async def update_proyecto(
    proyecto_id: str,
    proyecto_data: ProyectoUpdate,
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Actualiza un proyecto existente.

    - **proyecto_id**: ID del proyecto a actualizar
    - Solo se actualizan los campos proporcionados
    """
    return service.update_proyecto(proyecto_id, proyecto_data)


@router.delete(
    "/{proyecto_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar proyecto",
    description="Elimina un proyecto"
)
async def delete_proyecto(
    proyecto_id: str,
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Elimina un proyecto.

    - **proyecto_id**: ID del proyecto a eliminar

    Nota: En futuro se validará que no tenga gastos asociados.
    """
    return service.delete_proyecto(proyecto_id)


@router.get(
    "/{proyecto_id}/resumen",
    response_model=ProyectoResumen,
    summary="Resumen financiero del proyecto",
    description="Obtiene un resumen del estado financiero del proyecto"
)
async def get_resumen_financiero(
    proyecto_id: str,
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Obtiene el resumen financiero de un proyecto.

    Incluye:
    - Presupuesto total
    - Total gastado
    - Porcentaje gastado
    - Balance restante
    - Alertas si está cerca del límite
    """
    return service.get_resumen_financiero(proyecto_id)


@router.get(
    "/stats/general",
    summary="Estadísticas generales",
    description="Obtiene estadísticas generales de proyectos"
)
async def get_estadisticas(
    service: ProyectoService = Depends(get_proyecto_service)
):
    """
    Obtiene estadísticas generales de todos los proyectos.

    Incluye:
    - Total de proyectos
    - Conteo por estado
    """
    return service.get_estadisticas()
