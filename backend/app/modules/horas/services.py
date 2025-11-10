"""
Servicios de Horas
"""
from typing import List, Optional
from datetime import date
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.horas.models import RegistroHora
from app.modules.horas.schemas import (
    RegistroHoraCreate,
    RegistroHoraUpdate,
    RegistroHoraResponse,
    RegistroHoraStatsResponse,
    ResumenHorasEmpleado,
    ResumenHorasProyecto
)
from app.modules.horas.repository import RegistroHoraRepository
from app.modules.personal.repository import EmpleadoRepository
from app.modules.proyectos.repository import ProyectoRepository
from app.modules.tareas.repository import TareaRepository


class RegistroHoraService:
    """Servicio para lógica de negocio de Registros de Horas"""

    def __init__(self, db: Session):
        self.repository = RegistroHoraRepository(db)
        self.empleado_repository = EmpleadoRepository(db)
        self.proyecto_repository = ProyectoRepository(db)
        self.tarea_repository = TareaRepository(db)
        self.db = db

    def get_registro_by_id(self, registro_id: str) -> RegistroHoraResponse:
        """Obtiene un registro por ID"""
        registro = self.repository.get_by_id(registro_id)

        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con ID {registro_id} no encontrado"
            )

        return self._to_response(registro)

    def get_registros(
        self,
        skip: int = 0,
        limit: int = 50,
        empleado_id: Optional[str] = None,
        proyecto_id: Optional[str] = None,
        tarea_id: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> tuple[List[RegistroHoraResponse], int]:
        """Obtiene lista de registros con filtros"""
        registros, total = self.repository.get_all(
            skip=skip,
            limit=limit,
            empleado_id=empleado_id,
            proyecto_id=proyecto_id,
            tarea_id=tarea_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta
        )

        return [self._to_response(reg) for reg in registros], total

    def create_registro(self, registro_data: RegistroHoraCreate) -> RegistroHoraResponse:
        """Crea un nuevo registro de horas"""
        # Validar que el empleado existe y está activo
        empleado = self.empleado_repository.get_by_id(registro_data.empleado_id)
        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado con ID {registro_data.empleado_id} no encontrado"
            )
        if not empleado.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El empleado {empleado.nombre_completo} no está activo"
            )

        # Validar que el proyecto existe
        proyecto = self.proyecto_repository.get_by_id(registro_data.proyecto_id)
        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {registro_data.proyecto_id} no encontrado"
            )

        # Validar tarea si se proporciona
        if registro_data.tarea_id:
            tarea = self.tarea_repository.get_by_id(registro_data.tarea_id)
            if not tarea:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tarea con ID {registro_data.tarea_id} no encontrada"
                )
            # Validar que la tarea pertenece al proyecto
            if tarea.proyecto_id != registro_data.proyecto_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La tarea no pertenece al proyecto especificado"
                )

        # Validar datos de negocio
        self._validar_registro_data(registro_data)

        # Crear registro
        registro = self.repository.create(registro_data)

        return self._to_response(registro)

    def update_registro(self, registro_id: str, registro_data: RegistroHoraUpdate) -> RegistroHoraResponse:
        """Actualiza un registro existente"""
        registro = self.repository.get_by_id(registro_id)

        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con ID {registro_id} no encontrado"
            )

        # Validar tarea si se está actualizando
        if registro_data.tarea_id:
            tarea = self.tarea_repository.get_by_id(registro_data.tarea_id)
            if not tarea:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Tarea con ID {registro_data.tarea_id} no encontrada"
                )
            # Validar que la tarea pertenece al proyecto del registro
            if tarea.proyecto_id != registro.proyecto_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La tarea no pertenece al proyecto del registro"
                )

        # Actualizar registro
        registro_actualizado = self.repository.update(registro, registro_data)

        return self._to_response(registro_actualizado)

    def delete_registro(self, registro_id: str) -> dict:
        """Elimina un registro"""
        registro = self.repository.get_by_id(registro_id)

        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro con ID {registro_id} no encontrado"
            )

        self.repository.delete(registro)
        return {"message": f"Registro de {registro.horas} horas eliminado exitosamente"}

    def get_stats(
        self,
        empleado_id: Optional[str] = None,
        proyecto_id: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> RegistroHoraStatsResponse:
        """Obtiene estadísticas de registros de horas"""
        stats = self.repository.get_stats(empleado_id, proyecto_id, fecha_desde, fecha_hasta)
        return RegistroHoraStatsResponse(**stats)

    def get_resumen_por_empleado(
        self,
        proyecto_id: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[ResumenHorasEmpleado]:
        """Obtiene resumen de horas por empleado"""
        resumenes = self.repository.get_resumen_por_empleado(proyecto_id, fecha_desde, fecha_hasta)
        return [ResumenHorasEmpleado(**resumen) for resumen in resumenes]

    def get_resumen_por_proyecto(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[ResumenHorasProyecto]:
        """Obtiene resumen de horas por proyecto"""
        resumenes = self.repository.get_resumen_por_proyecto(fecha_desde, fecha_hasta)
        return [ResumenHorasProyecto(**resumen) for resumen in resumenes]

    def get_total_horas_empleado(
        self,
        empleado_id: str,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> dict:
        """Obtiene el total de horas de un empleado"""
        total = self.repository.get_total_horas_empleado(empleado_id, fecha_desde, fecha_hasta)
        return {
            "empleado_id": empleado_id,
            "total_horas": total,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }

    def get_total_horas_proyecto(
        self,
        proyecto_id: str,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> dict:
        """Obtiene el total de horas de un proyecto"""
        total = self.repository.get_total_horas_proyecto(proyecto_id, fecha_desde, fecha_hasta)
        return {
            "proyecto_id": proyecto_id,
            "total_horas": total,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta
        }

    def _validar_registro_data(self, registro_data: RegistroHoraCreate) -> None:
        """Valida los datos de negocio del registro"""
        # Las validaciones básicas ya están en el schema (fecha no futura, horas entre 0.5 y 24)
        # Aquí se pueden agregar validaciones adicionales de negocio

        # Por ejemplo: validar que no haya múltiples registros del mismo empleado en la misma fecha
        # para el mismo proyecto (esto depende de los requisitos del negocio)
        pass

    def _to_response(self, registro: RegistroHora) -> RegistroHoraResponse:
        """Convierte un modelo RegistroHora a RegistroHoraResponse"""
        return RegistroHoraResponse.model_validate(registro)
