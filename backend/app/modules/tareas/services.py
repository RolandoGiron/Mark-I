"""
Servicios de Tareas
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.tareas.models import Tarea
from app.modules.tareas.schemas import (
    TareaCreate,
    TareaUpdate,
    TareaResponse,
    CambiarEstadoTarea,
    TareaStatsResponse
)
from app.modules.tareas.repository import TareaRepository
from app.modules.proyectos.repository import ProyectoRepository
from app.modules.auth.repository import UsuarioRepository


class TareaService:
    """Servicio para lógica de negocio de Tareas"""

    def __init__(self, db: Session):
        self.repository = TareaRepository(db)
        self.proyecto_repository = ProyectoRepository(db)
        self.usuario_repository = UsuarioRepository(db)
        self.db = db

    def get_tarea_by_id(self, tarea_id: str) -> TareaResponse:
        """Obtiene una tarea por ID"""
        tarea = self.repository.get_by_id(tarea_id)

        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID {tarea_id} no encontrada"
            )

        return self._to_response(tarea)

    def get_tareas(
        self,
        skip: int = 0,
        limit: int = 50,
        proyecto_id: Optional[str] = None,
        asignado_a_id: Optional[str] = None,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[TareaResponse], int]:
        """Obtiene lista de tareas con filtros"""
        tareas, total = self.repository.get_all(
            skip=skip,
            limit=limit,
            proyecto_id=proyecto_id,
            asignado_a_id=asignado_a_id,
            estado=estado,
            prioridad=prioridad,
            search=search
        )

        return [self._to_response(tarea) for tarea in tareas], total

    def create_tarea(self, tarea_data: TareaCreate, creado_por_id: str) -> TareaResponse:
        """Crea una nueva tarea"""
        # Validar que el proyecto existe
        proyecto = self.proyecto_repository.get_by_id(tarea_data.proyecto_id)
        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {tarea_data.proyecto_id} no encontrado"
            )

        # Validar que el usuario asignado existe si se proporciona
        if tarea_data.asignado_a_id:
            usuario = self.usuario_repository.get_by_id(tarea_data.asignado_a_id)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuario con ID {tarea_data.asignado_a_id} no encontrado"
                )

        # Validar datos de negocio
        self._validar_tarea_data(tarea_data)

        # Crear tarea
        tarea = self.repository.create(tarea_data, creado_por_id)

        return self._to_response(tarea)

    def update_tarea(self, tarea_id: str, tarea_data: TareaUpdate) -> TareaResponse:
        """Actualiza una tarea existente"""
        tarea = self.repository.get_by_id(tarea_id)

        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID {tarea_id} no encontrada"
            )

        # Validar usuario asignado si se está actualizando
        if tarea_data.asignado_a_id:
            usuario = self.usuario_repository.get_by_id(tarea_data.asignado_a_id)
            if not usuario:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuario con ID {tarea_data.asignado_a_id} no encontrado"
                )

        # Actualizar tarea
        tarea_actualizada = self.repository.update(tarea, tarea_data)

        return self._to_response(tarea_actualizada)

    def delete_tarea(self, tarea_id: str) -> dict:
        """Elimina una tarea"""
        tarea = self.repository.get_by_id(tarea_id)

        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID {tarea_id} no encontrada"
            )

        self.repository.delete(tarea)
        return {"message": f"Tarea '{tarea.titulo}' eliminada exitosamente"}

    def cambiar_estado(self, tarea_id: str, estado_data: CambiarEstadoTarea) -> TareaResponse:
        """Cambia el estado de una tarea"""
        tarea = self.repository.get_by_id(tarea_id)

        if not tarea:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tarea con ID {tarea_id} no encontrada"
            )

        tarea_actualizada = self.repository.cambiar_estado(tarea, estado_data.estado)

        return self._to_response(tarea_actualizada)

    def get_tareas_hoy(self, usuario_id: Optional[str] = None) -> List[TareaResponse]:
        """Obtiene las tareas que vencen hoy"""
        tareas = self.repository.get_tareas_hoy(usuario_id)
        return [self._to_response(tarea) for tarea in tareas]

    def get_tareas_vencidas(self, usuario_id: Optional[str] = None) -> List[TareaResponse]:
        """Obtiene las tareas vencidas"""
        tareas = self.repository.get_tareas_vencidas(usuario_id)
        return [self._to_response(tarea) for tarea in tareas]

    def get_mis_tareas(self, usuario_id: str, solo_activas: bool = True) -> List[TareaResponse]:
        """Obtiene las tareas asignadas a un usuario"""
        tareas = self.repository.get_by_usuario(usuario_id, solo_activas)
        return [self._to_response(tarea) for tarea in tareas]

    def get_stats(self, proyecto_id: Optional[str] = None) -> TareaStatsResponse:
        """Obtiene estadísticas de tareas"""
        stats = self.repository.get_stats(proyecto_id)
        return TareaStatsResponse(**stats)

    def _validar_tarea_data(self, tarea_data: TareaCreate) -> None:
        """Valida los datos de negocio de la tarea"""
        # Validar que el título no esté vacío
        if not tarea_data.titulo.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El título de la tarea no puede estar vacío"
            )

        # Validar que la fecha de vencimiento no sea en el pasado (si se proporciona)
        if tarea_data.fecha_vencimiento:
            from datetime import datetime
            if tarea_data.fecha_vencimiento < datetime.utcnow():
                # Permitir fechas del pasado, solo advertir (no bloquear)
                pass

        # Validar que fecha_inicio no sea posterior a fecha_vencimiento
        if tarea_data.fecha_inicio and tarea_data.fecha_vencimiento:
            if tarea_data.fecha_inicio > tarea_data.fecha_vencimiento:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha de inicio no puede ser posterior a la fecha de vencimiento"
                )

    def _to_response(self, tarea: Tarea) -> TareaResponse:
        """Convierte un modelo Tarea a TareaResponse"""
        return TareaResponse.model_validate(tarea)
