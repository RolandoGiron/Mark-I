"""
Rutas de Notificaciones
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.notificaciones.schemas import (
    NotificacionCreate,
    NotificacionUpdate,
    NotificacionResponse,
    NotificacionListResponse,
    NotificacionStatsResponse
)
from app.modules.notificaciones.services import NotificacionService
from app.modules.auth.models import Usuario
from app.shared.dependencies import get_current_active_user, require_admin

router = APIRouter(prefix="/notificaciones")


def get_notificacion_service(db: Session = Depends(get_db)) -> NotificacionService:
    """Dependency para obtener el servicio de notificaciones"""
    return NotificacionService(db)


@router.get("", response_model=NotificacionListResponse)
async def list_notificaciones(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=100, description="Tamaño de página"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    leida: Optional[bool] = Query(None, description="Filtrar por estado de lectura"),
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene lista de notificaciones del usuario actual con paginación y filtros

    - **page**: Número de página (default: 1)
    - **page_size**: Cantidad de items por página (default: 50, max: 100)
    - **tipo**: Filtrar por tipo de notificación
    - **leida**: Filtrar por estado (true = leídas, false = no leídas)
    """
    skip = (page - 1) * page_size
    notificaciones, total, no_leidas = service.get_notificaciones(
        skip=skip,
        limit=page_size,
        usuario_id=current_user.id,
        tipo=tipo,
        leida=leida
    )

    return NotificacionListResponse(
        total=total,
        no_leidas=no_leidas,
        items=notificaciones,
        page=page,
        page_size=page_size
    )


@router.get("/stats", response_model=NotificacionStatsResponse)
async def get_notificaciones_stats(
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas de notificaciones del usuario actual

    Retorna:
    - Total de notificaciones
    - Notificaciones leídas y no leídas
    - Cantidad por tipo
    - Notificaciones de las últimas 24 horas
    """
    return service.get_stats(current_user.id)


@router.get("/recientes", response_model=list[NotificacionResponse])
async def get_notificaciones_recientes(
    horas: int = Query(24, ge=1, le=168, description="Horas hacia atrás (default: 24, max: 168)"),
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene las notificaciones recientes del usuario actual

    - **horas**: Cantidad de horas hacia atrás (default: 24, max: 168)
    """
    return service.get_recientes(current_user.id, horas)


@router.get("/{notificacion_id}", response_model=NotificacionResponse)
async def get_notificacion(
    notificacion_id: str,
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene una notificación por ID

    - **notificacion_id**: ID de la notificación
    """
    return service.get_notificacion_by_id(notificacion_id)


@router.post("", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
async def create_notificacion(
    notificacion_data: NotificacionCreate,
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(require_admin)
):
    """
    Crea una nueva notificación (solo administradores)

    - **usuario_id**: ID del usuario destinatario
    - **tipo**: Tipo de notificación
    - **titulo**: Título de la notificación
    - **mensaje**: Mensaje de la notificación
    - **datos**: Datos adicionales (opcional, JSON)
    """
    return service.create_notificacion(notificacion_data)


@router.patch("/{notificacion_id}", response_model=NotificacionResponse)
async def update_notificacion(
    notificacion_id: str,
    notificacion_data: NotificacionUpdate,
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza el estado de una notificación (marcar como leída/no leída)

    - **notificacion_id**: ID de la notificación
    - **leida**: true para marcar como leída, false para no leída
    """
    return service.update_notificacion(notificacion_id, notificacion_data)


@router.post("/{notificacion_id}/leer", response_model=NotificacionResponse)
async def marcar_como_leida(
    notificacion_id: str,
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Marca una notificación como leída

    - **notificacion_id**: ID de la notificación
    """
    return service.marcar_como_leida(notificacion_id)


@router.post("/leer-todas")
async def marcar_todas_leidas(
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Marca todas las notificaciones del usuario actual como leídas
    """
    return service.marcar_todas_leidas(current_user.id)


@router.delete("/{notificacion_id}")
async def delete_notificacion(
    notificacion_id: str,
    service: NotificacionService = Depends(get_notificacion_service),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Elimina una notificación

    - **notificacion_id**: ID de la notificación a eliminar
    """
    return service.delete_notificacion(notificacion_id)
