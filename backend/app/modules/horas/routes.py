"""
Rutas de Horas
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.horas.schemas import (
    RegistroHoraCreate,
    RegistroHoraUpdate,
    RegistroHoraResponse,
    RegistroHoraListResponse,
    RegistroHoraStatsResponse,
    ResumenHorasEmpleado,
    ResumenHorasProyecto
)
from app.modules.horas.services import RegistroHoraService
from app.modules.auth.models import Usuario
from app.shared.dependencies import get_current_active_user

router = APIRouter(prefix="/horas")


def get_registro_hora_service(db: Session = Depends(get_db)) -> RegistroHoraService:
    """Dependency para obtener el servicio de registros de horas"""
    return RegistroHoraService(db)


@router.get("", response_model=RegistroHoraListResponse)
async def list_registros(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    empleado_id: Optional[str] = Query(None, description="Filtrar por empleado"),
    proyecto_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    tarea_id: Optional[str] = Query(None, description="Filtrar por tarea"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicial del rango"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha final del rango"),
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene lista de registros de horas con paginación y filtros

    - **page**: Número de página (default: 1)
    - **page_size**: Cantidad de items por página (default: 50, max: 100)
    - **empleado_id**: Filtrar por empleado
    - **proyecto_id**: Filtrar por proyecto
    - **tarea_id**: Filtrar por tarea
    - **fecha_desde**: Fecha inicial del rango
    - **fecha_hasta**: Fecha final del rango
    """
    skip = (page - 1) * page_size
    registros, total = service.get_registros(
        skip=skip,
        limit=page_size,
        empleado_id=empleado_id,
        proyecto_id=proyecto_id,
        tarea_id=tarea_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )

    return RegistroHoraListResponse(
        total=total,
        items=registros,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=RegistroHoraStatsResponse)
async def get_registros_stats(
    empleado_id: Optional[str] = Query(None, description="Filtrar por empleado"),
    proyecto_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicial del rango"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha final del rango"),
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas de registros de horas

    Retorna:
    - Total de registros
    - Total de horas trabajadas
    - Total de horas extras
    - Promedio de horas por día
    - Días trabajados
    """
    return service.get_stats(empleado_id, proyecto_id, fecha_desde, fecha_hasta)


@router.get("/resumen/empleados", response_model=list[ResumenHorasEmpleado])
async def get_resumen_por_empleado(
    proyecto_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicial del rango"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha final del rango"),
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene resumen de horas trabajadas agrupado por empleado

    Incluye:
    - Total de horas por empleado
    - Horas extras
    - Días trabajados
    - Costo total (horas × tarifa)
    """
    return service.get_resumen_por_empleado(proyecto_id, fecha_desde, fecha_hasta)


@router.get("/resumen/proyectos", response_model=list[ResumenHorasProyecto])
async def get_resumen_por_proyecto(
    fecha_desde: Optional[date] = Query(None, description="Fecha inicial del rango"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha final del rango"),
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene resumen de horas trabajadas agrupado por proyecto

    Incluye:
    - Total de horas por proyecto
    - Horas extras
    - Cantidad de empleados
    - Costo de mano de obra
    """
    return service.get_resumen_por_proyecto(fecha_desde, fecha_hasta)


@router.get("/empleado/{empleado_id}/total")
async def get_total_horas_empleado(
    empleado_id: str,
    fecha_desde: Optional[date] = Query(None, description="Fecha inicial del rango"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha final del rango"),
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene el total de horas de un empleado en un periodo

    - **empleado_id**: ID del empleado
    - **fecha_desde**: Fecha inicial (opcional)
    - **fecha_hasta**: Fecha final (opcional)
    """
    return service.get_total_horas_empleado(empleado_id, fecha_desde, fecha_hasta)


@router.get("/proyecto/{proyecto_id}/total")
async def get_total_horas_proyecto(
    proyecto_id: str,
    fecha_desde: Optional[date] = Query(None, description="Fecha inicial del rango"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha final del rango"),
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene el total de horas de un proyecto en un periodo

    - **proyecto_id**: ID del proyecto
    - **fecha_desde**: Fecha inicial (opcional)
    - **fecha_hasta**: Fecha final (opcional)
    """
    return service.get_total_horas_proyecto(proyecto_id, fecha_desde, fecha_hasta)


@router.get("/{registro_id}", response_model=RegistroHoraResponse)
async def get_registro(
    registro_id: str,
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene un registro por ID

    - **registro_id**: ID del registro
    """
    return service.get_registro_by_id(registro_id)


@router.post("", response_model=RegistroHoraResponse, status_code=status.HTTP_201_CREATED)
async def create_registro(
    registro_data: RegistroHoraCreate,
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crea un nuevo registro de horas

    - **empleado_id**: ID del empleado
    - **proyecto_id**: ID del proyecto
    - **tarea_id**: ID de la tarea (opcional)
    - **fecha**: Fecha del registro
    - **horas**: Cantidad de horas (0.5 a 24)
    - **descripcion**: Descripción del trabajo (opcional)
    """
    return service.create_registro(registro_data)


@router.put("/{registro_id}", response_model=RegistroHoraResponse)
async def update_registro(
    registro_id: str,
    registro_data: RegistroHoraUpdate,
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza un registro existente

    - **registro_id**: ID del registro a actualizar
    - Todos los campos son opcionales
    """
    return service.update_registro(registro_id, registro_data)


@router.delete("/{registro_id}")
async def delete_registro(
    registro_id: str,
    service: RegistroHoraService = Depends(get_registro_hora_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina un registro

    - **registro_id**: ID del registro a eliminar
    """
    return service.delete_registro(registro_id)
