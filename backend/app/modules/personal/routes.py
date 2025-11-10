"""
Rutas de Personal
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.personal.schemas import (
    EmpleadoCreate,
    EmpleadoUpdate,
    EmpleadoResponse,
    EmpleadoListResponse,
    EmpleadoStatsResponse
)
from app.modules.personal.services import EmpleadoService
from app.modules.auth.models import Usuario
from app.shared.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/personal")


def get_empleado_service(db: Session = Depends(get_db)) -> EmpleadoService:
    """Dependency para obtener el servicio de empleados"""
    return EmpleadoService(db)


@router.get("", response_model=EmpleadoListResponse)
async def list_empleados(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    cargo: Optional[str] = Query(None, description="Filtrar por cargo"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    search: Optional[str] = Query(None, description="Buscar por nombre, apellido o documento"),
    service: EmpleadoService = Depends(get_empleado_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene lista de empleados con paginación y filtros

    - **page**: Número de página (default: 1)
    - **page_size**: Cantidad de items por página (default: 50, max: 100)
    - **cargo**: Filtrar por cargo
    - **activo**: Filtrar por estado activo (true/false)
    - **search**: Buscar por nombre, apellido o documento
    """
    skip = (page - 1) * page_size
    empleados, total = service.get_empleados(
        skip=skip,
        limit=page_size,
        cargo=cargo,
        activo=activo,
        search=search
    )

    return EmpleadoListResponse(
        total=total,
        items=empleados,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=EmpleadoStatsResponse)
async def get_empleados_stats(
    service: EmpleadoService = Depends(get_empleado_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas de empleados

    Retorna:
    - Total de empleados
    - Empleados activos e inactivos
    - Cantidad por cargo
    - Tarifa promedio por hora
    """
    return service.get_stats()


@router.get("/{empleado_id}", response_model=EmpleadoResponse)
async def get_empleado(
    empleado_id: str,
    service: EmpleadoService = Depends(get_empleado_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un empleado por ID

    - **empleado_id**: ID del empleado
    """
    return service.get_empleado_by_id(empleado_id)


@router.get("/documento/{documento}", response_model=EmpleadoResponse)
async def get_empleado_by_documento(
    documento: str,
    service: EmpleadoService = Depends(get_empleado_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un empleado por documento de identidad

    - **documento**: Documento de identidad del empleado
    """
    return service.get_empleado_by_documento(documento)


@router.post("", response_model=EmpleadoResponse, status_code=status.HTTP_201_CREATED)
async def create_empleado(
    empleado_data: EmpleadoCreate,
    service: EmpleadoService = Depends(get_empleado_service),
    current_user: Usuario = Depends(require_admin)
):
    """
    Crea un nuevo empleado

    Requiere rol de administrador.

    - **nombre**: Nombre del empleado
    - **apellido**: Apellido del empleado
    - **cargo**: Cargo del empleado
    - **tarifa_hora**: Tarifa por hora
    - **documento_identidad**: Documento de identidad (opcional)
    - **telefono**: Teléfono (opcional)
    - **email**: Email (opcional)
    - **fecha_ingreso**: Fecha de ingreso (opcional)
    - **usuario_id**: ID de usuario asociado (opcional)
    - **notas**: Notas adicionales (opcional)
    """
    return service.create_empleado(empleado_data)


@router.put("/{empleado_id}", response_model=EmpleadoResponse)
async def update_empleado(
    empleado_id: str,
    empleado_data: EmpleadoUpdate,
    service: EmpleadoService = Depends(get_empleado_service),
    current_user: Usuario = Depends(require_admin)
):
    """
    Actualiza un empleado existente

    Requiere rol de administrador.

    - **empleado_id**: ID del empleado a actualizar
    - Todos los campos son opcionales
    """
    return service.update_empleado(empleado_id, empleado_data)


@router.delete("/{empleado_id}")
async def delete_empleado(
    empleado_id: str,
    hard_delete: bool = Query(False, description="Eliminar permanentemente (true) o marcar como inactivo (false)"),
    service: EmpleadoService = Depends(get_empleado_service),
    current_user: Usuario = Depends(require_admin)
):
    """
    Elimina un empleado

    Requiere rol de administrador.

    - **empleado_id**: ID del empleado a eliminar
    - **hard_delete**: Si es true, elimina permanentemente. Si es false (default), marca como inactivo.
    """
    return service.delete_empleado(empleado_id, hard_delete=hard_delete)
