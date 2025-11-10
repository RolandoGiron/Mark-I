"""
Rutas de Tareas
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.tareas.schemas import (
    TareaCreate,
    TareaUpdate,
    TareaResponse,
    TareaListResponse,
    CambiarEstadoTarea,
    TareaStatsResponse
)
from app.modules.tareas.services import TareaService
from app.modules.auth.models import Usuario
from app.shared.dependencies import get_current_active_user

router = APIRouter(prefix="/tareas")


def get_tarea_service(db: Session = Depends(get_db)) -> TareaService:
    """Dependency para obtener el servicio de tareas"""
    return TareaService(db)


@router.get("", response_model=TareaListResponse)
async def list_tareas(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    proyecto_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    asignado_a_id: Optional[str] = Query(None, description="Filtrar por usuario asignado"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    prioridad: Optional[str] = Query(None, description="Filtrar por prioridad"),
    search: Optional[str] = Query(None, description="Buscar por título o descripción"),
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene lista de tareas con paginación y filtros

    - **page**: Número de página (default: 1)
    - **page_size**: Cantidad de items por página (default: 50, max: 100)
    - **proyecto_id**: Filtrar por proyecto
    - **asignado_a_id**: Filtrar por usuario asignado
    - **estado**: Filtrar por estado (pendiente, en_progreso, completada, cancelada)
    - **prioridad**: Filtrar por prioridad (baja, media, alta, urgente)
    - **search**: Buscar por título o descripción
    """
    skip = (page - 1) * page_size
    tareas, total = service.get_tareas(
        skip=skip,
        limit=page_size,
        proyecto_id=proyecto_id,
        asignado_a_id=asignado_a_id,
        estado=estado,
        prioridad=prioridad,
        search=search
    )

    return TareaListResponse(
        total=total,
        items=tareas,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=TareaStatsResponse)
async def get_tareas_stats(
    proyecto_id: Optional[str] = Query(None, description="Filtrar por proyecto"),
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas de tareas

    - **proyecto_id**: Opcional, filtrar estadísticas por proyecto

    Retorna:
    - Total de tareas
    - Cantidad por estado
    - Cantidad por prioridad
    - Tareas vencidas
    - Tareas que vencen hoy
    """
    return service.get_stats(proyecto_id)


@router.get("/hoy", response_model=list[TareaResponse])
async def get_tareas_hoy(
    usuario_id: Optional[str] = Query(None, description="Filtrar por usuario asignado"),
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene las tareas que vencen hoy

    - **usuario_id**: Opcional, filtrar por usuario asignado
    """
    return service.get_tareas_hoy(usuario_id)


@router.get("/vencidas", response_model=list[TareaResponse])
async def get_tareas_vencidas(
    usuario_id: Optional[str] = Query(None, description="Filtrar por usuario asignado"),
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene las tareas vencidas

    - **usuario_id**: Opcional, filtrar por usuario asignado
    """
    return service.get_tareas_vencidas(usuario_id)


@router.get("/mis-tareas", response_model=list[TareaResponse])
async def get_mis_tareas(
    solo_activas: bool = Query(True, description="Solo tareas activas (no completadas ni canceladas)"),
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene las tareas asignadas al usuario actual

    - **solo_activas**: Si es true, solo retorna tareas pendientes o en progreso
    """
    return service.get_mis_tareas(current_user.id, solo_activas)


@router.get("/{tarea_id}", response_model=TareaResponse)
async def get_tarea(
    tarea_id: str,
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene una tarea por ID

    - **tarea_id**: ID de la tarea
    """
    return service.get_tarea_by_id(tarea_id)


@router.post("", response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
async def create_tarea(
    tarea_data: TareaCreate,
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Crea una nueva tarea

    - **titulo**: Título de la tarea
    - **descripcion**: Descripción detallada (opcional)
    - **proyecto_id**: ID del proyecto
    - **asignado_a_id**: ID del usuario asignado (opcional)
    - **estado**: Estado (default: pendiente)
    - **prioridad**: Prioridad (default: media)
    - **fecha_vencimiento**: Fecha de vencimiento (opcional)
    - **fecha_inicio**: Fecha de inicio (opcional)
    """
    return service.create_tarea(tarea_data, current_user.id)


@router.put("/{tarea_id}", response_model=TareaResponse)
async def update_tarea(
    tarea_id: str,
    tarea_data: TareaUpdate,
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza una tarea existente

    - **tarea_id**: ID de la tarea a actualizar
    - Todos los campos son opcionales
    """
    return service.update_tarea(tarea_id, tarea_data)


@router.patch("/{tarea_id}/estado", response_model=TareaResponse)
async def cambiar_estado_tarea(
    tarea_id: str,
    estado_data: CambiarEstadoTarea,
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cambia el estado de una tarea

    - **tarea_id**: ID de la tarea
    - **estado**: Nuevo estado (pendiente, en_progreso, completada, cancelada)
    """
    return service.cambiar_estado(tarea_id, estado_data)


@router.delete("/{tarea_id}")
async def delete_tarea(
    tarea_id: str,
    service: TareaService = Depends(get_tarea_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina una tarea

    - **tarea_id**: ID de la tarea a eliminar
    """
    return service.delete_tarea(tarea_id)
