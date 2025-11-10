"""
Servicios de Notificaciones
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.notificaciones.models import Notificacion
from app.modules.notificaciones.schemas import (
    NotificacionCreate,
    NotificacionUpdate,
    NotificacionResponse,
    NotificacionStatsResponse
)
from app.modules.notificaciones.repository import NotificacionRepository


class NotificacionService:
    """Servicio para lógica de negocio de Notificaciones"""

    def __init__(self, db: Session):
        self.repository = NotificacionRepository(db)
        self.db = db

    def get_notificacion_by_id(self, notificacion_id: str) -> NotificacionResponse:
        """Obtiene una notificación por ID"""
        notificacion = self.repository.get_by_id(notificacion_id)

        if not notificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notificación con ID {notificacion_id} no encontrada"
            )

        return self._to_response(notificacion)

    def get_notificaciones(
        self,
        skip: int = 0,
        limit: int = 50,
        usuario_id: Optional[str] = None,
        tipo: Optional[str] = None,
        leida: Optional[bool] = None
    ) -> tuple[List[NotificacionResponse], int, int]:
        """Obtiene lista de notificaciones con filtros"""
        notificaciones, total = self.repository.get_all(
            skip=skip,
            limit=limit,
            usuario_id=usuario_id,
            tipo=tipo,
            leida=leida
        )

        # Contar no leídas si se filtra por usuario
        no_leidas = 0
        if usuario_id:
            no_leidas = self.repository.count_no_leidas(usuario_id)

        return [self._to_response(notif) for notif in notificaciones], total, no_leidas

    def create_notificacion(self, notificacion_data: NotificacionCreate) -> NotificacionResponse:
        """Crea una nueva notificación"""
        # Validar datos de negocio
        self._validar_notificacion_data(notificacion_data)

        # Crear notificación
        notificacion = self.repository.create(notificacion_data)

        return self._to_response(notificacion)

    def update_notificacion(
        self,
        notificacion_id: str,
        notificacion_data: NotificacionUpdate
    ) -> NotificacionResponse:
        """Actualiza una notificación"""
        notificacion = self.repository.get_by_id(notificacion_id)

        if not notificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notificación con ID {notificacion_id} no encontrada"
            )

        notificacion_actualizada = self.repository.update(notificacion, notificacion_data)

        return self._to_response(notificacion_actualizada)

    def marcar_como_leida(self, notificacion_id: str) -> NotificacionResponse:
        """Marca una notificación como leída"""
        notificacion = self.repository.get_by_id(notificacion_id)

        if not notificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notificación con ID {notificacion_id} no encontrada"
            )

        notificacion_actualizada = self.repository.marcar_como_leida(notificacion)

        return self._to_response(notificacion_actualizada)

    def marcar_todas_leidas(self, usuario_id: str) -> dict:
        """Marca todas las notificaciones de un usuario como leídas"""
        count = self.repository.marcar_todas_leidas(usuario_id)

        return {
            "message": f"{count} notificaciones marcadas como leídas",
            "cantidad": count
        }

    def delete_notificacion(self, notificacion_id: str) -> dict:
        """Elimina una notificación"""
        notificacion = self.repository.get_by_id(notificacion_id)

        if not notificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notificación con ID {notificacion_id} no encontrada"
            )

        self.repository.delete(notificacion)
        return {"message": "Notificación eliminada exitosamente"}

    def get_stats(self, usuario_id: str) -> NotificacionStatsResponse:
        """Obtiene estadísticas de notificaciones de un usuario"""
        stats = self.repository.get_stats(usuario_id)
        return NotificacionStatsResponse(**stats)

    def get_recientes(self, usuario_id: str, horas: int = 24) -> List[NotificacionResponse]:
        """Obtiene las notificaciones recientes (últimas X horas)"""
        notificaciones = self.repository.get_recientes(usuario_id, horas)
        return [self._to_response(notif) for notif in notificaciones]

    # Métodos helper para crear notificaciones específicas

    def crear_alerta_presupuesto(
        self,
        usuario_id: str,
        proyecto_id: str,
        proyecto_nombre: str,
        porcentaje_gastado: float
    ) -> NotificacionResponse:
        """Crea una alerta de presupuesto"""
        notificacion_data = NotificacionCreate(
            usuario_id=usuario_id,
            tipo="alerta_presupuesto",
            titulo=f"Alerta de presupuesto: {proyecto_nombre}",
            mensaje=f"El proyecto '{proyecto_nombre}' ha alcanzado el {porcentaje_gastado:.1f}% del presupuesto.",
            datos={"proyecto_id": proyecto_id, "porcentaje_gastado": porcentaje_gastado}
        )
        return self.create_notificacion(notificacion_data)

    def crear_tarea_asignada(
        self,
        usuario_id: str,
        tarea_id: str,
        tarea_titulo: str,
        proyecto_nombre: str
    ) -> NotificacionResponse:
        """Crea una notificación de tarea asignada"""
        notificacion_data = NotificacionCreate(
            usuario_id=usuario_id,
            tipo="tarea_asignada",
            titulo="Nueva tarea asignada",
            mensaje=f"Te han asignado la tarea '{tarea_titulo}' en el proyecto {proyecto_nombre}",
            datos={"tarea_id": tarea_id}
        )
        return self.create_notificacion(notificacion_data)

    def crear_tarea_vencida(
        self,
        usuario_id: str,
        tarea_id: str,
        tarea_titulo: str
    ) -> NotificacionResponse:
        """Crea una notificación de tarea vencida"""
        notificacion_data = NotificacionCreate(
            usuario_id=usuario_id,
            tipo="tarea_vencida",
            titulo="Tarea vencida",
            mensaje=f"La tarea '{tarea_titulo}' ha vencido y requiere tu atención",
            datos={"tarea_id": tarea_id}
        )
        return self.create_notificacion(notificacion_data)

    def crear_gasto_pendiente(
        self,
        usuario_id: str,
        costo_id: str,
        monto: float,
        proyecto_nombre: str
    ) -> NotificacionResponse:
        """Crea una notificación de gasto pendiente de validación"""
        notificacion_data = NotificacionCreate(
            usuario_id=usuario_id,
            tipo="gasto_pendiente",
            titulo="Gasto pendiente de validación",
            mensaje=f"Hay un gasto de ${monto:.2f} en {proyecto_nombre} pendiente de validación",
            datos={"costo_id": costo_id}
        )
        return self.create_notificacion(notificacion_data)

    def _validar_notificacion_data(self, notificacion_data: NotificacionCreate) -> None:
        """Valida los datos de negocio de la notificación"""
        # Validar que el título y mensaje no estén vacíos
        if not notificacion_data.titulo.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El título no puede estar vacío"
            )

        if not notificacion_data.mensaje.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El mensaje no puede estar vacío"
            )

    def _to_response(self, notificacion: Notificacion) -> NotificacionResponse:
        """Convierte un modelo Notificacion a NotificacionResponse"""
        return NotificacionResponse.model_validate(notificacion)
