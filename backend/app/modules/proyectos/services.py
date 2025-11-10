"""
Servicios de lógica de negocio para el módulo Proyectos.
"""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

from app.modules.proyectos.models import Proyecto, EstadoProyecto
from app.modules.proyectos.schemas import (
    ProyectoCreate,
    ProyectoUpdate,
    ProyectoResponse,
    ProyectoResumen
)
from app.modules.proyectos.repository import ProyectoRepository


class ProyectoService:
    """Servicio para lógica de negocio de Proyectos"""

    def __init__(self, db: Session):
        self.repository = ProyectoRepository(db)
        self.db = db

    def get_proyecto_by_id(self, proyecto_id: str) -> ProyectoResponse:
        """Obtiene un proyecto por ID"""
        proyecto = self.repository.get_by_id(proyecto_id)

        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {proyecto_id} no encontrado"
            )

        return self._to_response(proyecto)

    def get_proyecto_by_codigo(self, codigo: str) -> ProyectoResponse:
        """Obtiene un proyecto por código"""
        proyecto = self.repository.get_by_codigo(codigo)

        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con código {codigo} no encontrado"
            )

        return self._to_response(proyecto)

    def get_proyectos(
        self,
        skip: int = 0,
        limit: int = 50,
        estado: Optional[EstadoProyecto] = None,
        cliente: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[ProyectoResponse], int]:
        """Obtiene lista de proyectos con filtros"""
        proyectos, total = self.repository.get_all(
            skip=skip,
            limit=limit,
            estado=estado,
            cliente=cliente,
            search=search
        )

        return [self._to_response(p) for p in proyectos], total

    def create_proyecto(self, proyecto_data: ProyectoCreate) -> ProyectoResponse:
        """Crea un nuevo proyecto"""
        # Verificar que el código no exista
        if self.repository.exists_codigo(proyecto_data.codigo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un proyecto con el código {proyecto_data.codigo}"
            )

        # Validaciones de negocio adicionales
        self._validar_proyecto_data(proyecto_data)

        # Crear proyecto
        proyecto = self.repository.create(proyecto_data)

        return self._to_response(proyecto)

    def update_proyecto(
        self,
        proyecto_id: str,
        proyecto_data: ProyectoUpdate
    ) -> ProyectoResponse:
        """Actualiza un proyecto existente"""
        proyecto = self.repository.get_by_id(proyecto_id)

        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {proyecto_id} no encontrado"
            )

        # Si se actualiza el código, verificar que no exista
        if proyecto_data.codigo and proyecto_data.codigo != proyecto.codigo:
            if self.repository.exists_codigo(proyecto_data.codigo, exclude_id=proyecto_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un proyecto con el código {proyecto_data.codigo}"
                )

        # Actualizar
        proyecto = self.repository.update(proyecto, proyecto_data)

        return self._to_response(proyecto)

    def delete_proyecto(self, proyecto_id: str) -> dict:
        """Elimina un proyecto"""
        proyecto = self.repository.get_by_id(proyecto_id)

        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {proyecto_id} no encontrado"
            )

        # Validar que se pueda eliminar (agregar lógica según reglas de negocio)
        # Por ejemplo, no permitir eliminar proyectos con gastos registrados
        # TODO: Agregar validación cuando exista módulo de Costos

        self.repository.delete(proyecto)

        return {"message": f"Proyecto {proyecto.codigo} eliminado exitosamente"}

    def get_resumen_financiero(self, proyecto_id: str) -> ProyectoResumen:
        """Obtiene el resumen financiero de un proyecto"""
        proyecto = self.repository.get_by_id(proyecto_id)

        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {proyecto_id} no encontrado"
            )

        # TODO: Calcular gastos reales cuando exista el módulo de Costos
        # Por ahora retornamos valores base
        total_gastado = Decimal("0.00")
        porcentaje_gastado = Decimal("0.00")
        balance = proyecto.presupuesto_total
        en_alerta = False

        # Cuando tengamos el módulo de costos:
        # total_gastado = self._calcular_total_gastado(proyecto_id)
        # porcentaje_gastado = (total_gastado / proyecto.presupuesto_total) * 100
        # balance = proyecto.presupuesto_total - total_gastado
        # en_alerta = porcentaje_gastado >= 90

        return ProyectoResumen(
            id=proyecto.id,
            codigo=proyecto.codigo,
            nombre=proyecto.nombre,
            presupuesto_total=proyecto.presupuesto_total,
            total_gastado=total_gastado,
            porcentaje_gastado=porcentaje_gastado,
            balance=balance,
            estado=proyecto.estado,
            en_alerta=en_alerta
        )

    def get_estadisticas(self) -> dict:
        """Obtiene estadísticas generales de proyectos"""
        conteo_por_estado = self.repository.count_by_estado()

        return {
            "total_proyectos": sum(conteo_por_estado.values()),
            "por_estado": conteo_por_estado
        }

    def _validar_proyecto_data(self, proyecto_data: ProyectoCreate) -> None:
        """Validaciones de negocio adicionales"""
        # Ejemplo: Validar que el presupuesto sea razonable
        if proyecto_data.presupuesto_total > Decimal("100000000"):  # 100M
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El presupuesto parece excesivo. Verifica el monto."
            )

        # Ejemplo: Validar formato de código
        if not proyecto_data.codigo.replace("-", "").replace("_", "").isalnum():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código solo puede contener letras, números, guiones y guiones bajos"
            )

    def _to_response(self, proyecto: Proyecto) -> ProyectoResponse:
        """Convierte un modelo Proyecto a ProyectoResponse"""
        return ProyectoResponse(
            id=proyecto.id,
            codigo=proyecto.codigo,
            nombre=proyecto.nombre,
            cliente=proyecto.cliente,
            descripcion=proyecto.descripcion,
            presupuesto_total=proyecto.presupuesto_total,
            horas_presupuestadas=proyecto.horas_presupuestadas,
            fecha_inicio=proyecto.fecha_inicio,
            fecha_fin_estimada=proyecto.fecha_fin_estimada,
            fecha_fin_real=proyecto.fecha_fin_real,
            estado=proyecto.estado,
            datos_adicionales=proyecto.datos_adicionales,
            creado_en=proyecto.creado_en,
            actualizado_en=proyecto.actualizado_en,
            dias_transcurridos=proyecto.dias_transcurridos,
            dias_restantes=proyecto.dias_restantes
        )
