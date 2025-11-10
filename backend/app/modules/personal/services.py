"""
Servicios de Personal
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.modules.personal.models import Empleado
from app.modules.personal.schemas import (
    EmpleadoCreate,
    EmpleadoUpdate,
    EmpleadoResponse,
    EmpleadoStatsResponse
)
from app.modules.personal.repository import EmpleadoRepository


class EmpleadoService:
    """Servicio para lógica de negocio de Empleados"""

    def __init__(self, db: Session):
        self.repository = EmpleadoRepository(db)
        self.db = db

    def get_empleado_by_id(self, empleado_id: str) -> EmpleadoResponse:
        """Obtiene un empleado por ID"""
        empleado = self.repository.get_by_id(empleado_id)

        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado con ID {empleado_id} no encontrado"
            )

        return self._to_response(empleado)

    def get_empleados(
        self,
        skip: int = 0,
        limit: int = 50,
        cargo: Optional[str] = None,
        activo: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[EmpleadoResponse], int]:
        """Obtiene lista de empleados con filtros"""
        empleados, total = self.repository.get_all(
            skip=skip,
            limit=limit,
            cargo=cargo,
            activo=activo,
            search=search
        )

        return [self._to_response(emp) for emp in empleados], total

    def create_empleado(self, empleado_data: EmpleadoCreate) -> EmpleadoResponse:
        """Crea un nuevo empleado"""
        # Validar que no exista el documento si se proporciona
        if empleado_data.documento_identidad:
            if self.repository.exists_documento(empleado_data.documento_identidad):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un empleado con el documento {empleado_data.documento_identidad}"
                )

        # Validar usuario_id si se proporciona
        if empleado_data.usuario_id:
            empleado_existente = self.repository.get_by_usuario_id(empleado_data.usuario_id)
            if empleado_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El usuario ya está asociado al empleado {empleado_existente.nombre_completo}"
                )

        # Validar datos de negocio
        self._validar_empleado_data(empleado_data)

        # Crear empleado
        empleado = self.repository.create(empleado_data)

        return self._to_response(empleado)

    def update_empleado(self, empleado_id: str, empleado_data: EmpleadoUpdate) -> EmpleadoResponse:
        """Actualiza un empleado existente"""
        empleado = self.repository.get_by_id(empleado_id)

        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado con ID {empleado_id} no encontrado"
            )

        # Validar documento único si se está actualizando
        if empleado_data.documento_identidad:
            if self.repository.exists_documento(empleado_data.documento_identidad, exclude_id=empleado_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe otro empleado con el documento {empleado_data.documento_identidad}"
                )

        # Validar usuario_id si se está actualizando
        if empleado_data.usuario_id:
            empleado_existente = self.repository.get_by_usuario_id(empleado_data.usuario_id)
            if empleado_existente and empleado_existente.id != empleado_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El usuario ya está asociado a otro empleado"
                )

        # Actualizar empleado
        empleado_actualizado = self.repository.update(empleado, empleado_data)

        return self._to_response(empleado_actualizado)

    def delete_empleado(self, empleado_id: str, hard_delete: bool = False) -> dict:
        """Elimina un empleado (soft delete por defecto)"""
        empleado = self.repository.get_by_id(empleado_id)

        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado con ID {empleado_id} no encontrado"
            )

        if hard_delete:
            self.repository.hard_delete(empleado)
            return {"message": f"Empleado {empleado.nombre_completo} eliminado permanentemente"}
        else:
            self.repository.delete(empleado)
            return {"message": f"Empleado {empleado.nombre_completo} marcado como inactivo"}

    def get_empleado_by_documento(self, documento: str) -> EmpleadoResponse:
        """Obtiene un empleado por documento"""
        empleado = self.repository.get_by_documento(documento)

        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Empleado con documento {documento} no encontrado"
            )

        return self._to_response(empleado)

    def get_stats(self) -> EmpleadoStatsResponse:
        """Obtiene estadísticas de empleados"""
        stats = self.repository.get_stats()
        return EmpleadoStatsResponse(**stats)

    def _validar_empleado_data(self, empleado_data: EmpleadoCreate) -> None:
        """Valida los datos de negocio del empleado"""
        # Validar que la tarifa sea razonable (ejemplo: entre 0 y 100000)
        if empleado_data.tarifa_hora < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La tarifa por hora no puede ser negativa"
            )

        if empleado_data.tarifa_hora > 100000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La tarifa por hora parece excesiva. Verifique el valor."
            )

        # Validar que el nombre y apellido no estén vacíos
        if not empleado_data.nombre.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre no puede estar vacío"
            )

        if not empleado_data.apellido.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El apellido no puede estar vacío"
            )

    def _to_response(self, empleado: Empleado) -> EmpleadoResponse:
        """Convierte un modelo Empleado a EmpleadoResponse"""
        return EmpleadoResponse.model_validate(empleado)
