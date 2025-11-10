"""
Repository de Horas
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from app.modules.horas.models import RegistroHora
from app.modules.horas.schemas import RegistroHoraCreate, RegistroHoraUpdate


class RegistroHoraRepository:
    """Repository para operaciones de base de datos de Registros de Horas"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, registro_id: str) -> Optional[RegistroHora]:
        """Obtiene un registro por ID"""
        return self.db.query(RegistroHora).filter(RegistroHora.id == registro_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        empleado_id: Optional[str] = None,
        proyecto_id: Optional[str] = None,
        tarea_id: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> tuple[List[RegistroHora], int]:
        """
        Obtiene todos los registros con filtros opcionales

        Args:
            skip: Cantidad de registros a saltar
            limit: Cantidad máxima de registros a retornar
            empleado_id: Filtrar por empleado
            proyecto_id: Filtrar por proyecto
            tarea_id: Filtrar por tarea
            fecha_desde: Fecha inicial del rango
            fecha_hasta: Fecha final del rango

        Returns:
            Tupla con (lista de registros, total de registros)
        """
        query = self.db.query(RegistroHora)

        # Aplicar filtros
        if empleado_id:
            query = query.filter(RegistroHora.empleado_id == empleado_id)

        if proyecto_id:
            query = query.filter(RegistroHora.proyecto_id == proyecto_id)

        if tarea_id:
            query = query.filter(RegistroHora.tarea_id == tarea_id)

        if fecha_desde:
            query = query.filter(RegistroHora.fecha >= fecha_desde)

        if fecha_hasta:
            query = query.filter(RegistroHora.fecha <= fecha_hasta)

        # Obtener total
        total = query.count()

        # Aplicar paginación y ordenamiento
        registros = query.order_by(
            RegistroHora.fecha.desc(),
            RegistroHora.creado_en.desc()
        ).offset(skip).limit(limit).all()

        return registros, total

    def create(self, registro_data: RegistroHoraCreate) -> RegistroHora:
        """Crea un nuevo registro de horas"""
        registro = RegistroHora(**registro_data.model_dump())
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def update(self, registro: RegistroHora, registro_data: RegistroHoraUpdate) -> RegistroHora:
        """Actualiza un registro existente"""
        update_data = registro_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(registro, field, value)

        self.db.commit()
        self.db.refresh(registro)
        return registro

    def delete(self, registro: RegistroHora) -> bool:
        """Elimina un registro"""
        self.db.delete(registro)
        self.db.commit()
        return True

    def get_by_empleado_fecha(
        self,
        empleado_id: str,
        fecha_desde: date,
        fecha_hasta: date
    ) -> List[RegistroHora]:
        """Obtiene registros de un empleado en un rango de fechas"""
        return self.db.query(RegistroHora).filter(
            RegistroHora.empleado_id == empleado_id,
            RegistroHora.fecha >= fecha_desde,
            RegistroHora.fecha <= fecha_hasta
        ).order_by(RegistroHora.fecha.desc()).all()

    def get_by_proyecto_fecha(
        self,
        proyecto_id: str,
        fecha_desde: date,
        fecha_hasta: date
    ) -> List[RegistroHora]:
        """Obtiene registros de un proyecto en un rango de fechas"""
        return self.db.query(RegistroHora).filter(
            RegistroHora.proyecto_id == proyecto_id,
            RegistroHora.fecha >= fecha_desde,
            RegistroHora.fecha <= fecha_hasta
        ).order_by(RegistroHora.fecha.desc()).all()

    def get_total_horas_empleado(
        self,
        empleado_id: str,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Decimal:
        """Obtiene el total de horas de un empleado"""
        query = self.db.query(func.sum(RegistroHora.horas)).filter(
            RegistroHora.empleado_id == empleado_id
        )

        if fecha_desde:
            query = query.filter(RegistroHora.fecha >= fecha_desde)

        if fecha_hasta:
            query = query.filter(RegistroHora.fecha <= fecha_hasta)

        total = query.scalar()
        return Decimal(total) if total else Decimal('0')

    def get_total_horas_proyecto(
        self,
        proyecto_id: str,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> Decimal:
        """Obtiene el total de horas de un proyecto"""
        query = self.db.query(func.sum(RegistroHora.horas)).filter(
            RegistroHora.proyecto_id == proyecto_id
        )

        if fecha_desde:
            query = query.filter(RegistroHora.fecha >= fecha_desde)

        if fecha_hasta:
            query = query.filter(RegistroHora.fecha <= fecha_hasta)

        total = query.scalar()
        return Decimal(total) if total else Decimal('0')

    def get_stats(
        self,
        empleado_id: Optional[str] = None,
        proyecto_id: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> dict:
        """Obtiene estadísticas de registros de horas"""
        query = self.db.query(RegistroHora)

        # Aplicar filtros
        if empleado_id:
            query = query.filter(RegistroHora.empleado_id == empleado_id)

        if proyecto_id:
            query = query.filter(RegistroHora.proyecto_id == proyecto_id)

        if fecha_desde:
            query = query.filter(RegistroHora.fecha >= fecha_desde)

        if fecha_hasta:
            query = query.filter(RegistroHora.fecha <= fecha_hasta)

        # Total de registros
        total_registros = query.count()

        # Total de horas
        total_horas = query.with_entities(func.sum(RegistroHora.horas)).scalar() or Decimal('0')

        # Total de horas extras (horas > 8)
        registros = query.all()
        total_horas_extras = sum(
            float(r.horas) - 8.0 for r in registros if float(r.horas) > 8.0
        )

        # Días únicos trabajados
        dias_trabajados = query.with_entities(
            func.count(func.distinct(RegistroHora.fecha))
        ).scalar() or 0

        # Promedio de horas por día
        promedio_horas_dia = Decimal(total_horas) / dias_trabajados if dias_trabajados > 0 else Decimal('0')

        return {
            "total_registros": total_registros,
            "total_horas": Decimal(total_horas),
            "total_horas_extras": Decimal(str(total_horas_extras)),
            "promedio_horas_dia": promedio_horas_dia,
            "dias_trabajados": dias_trabajados
        }

    def get_resumen_por_empleado(
        self,
        proyecto_id: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[dict]:
        """Obtiene resumen de horas por empleado"""
        from app.modules.personal.models import Empleado

        query = self.db.query(
            RegistroHora.empleado_id,
            Empleado.nombre,
            Empleado.apellido,
            Empleado.tarifa_hora,
            func.sum(RegistroHora.horas).label('total_horas'),
            func.count(func.distinct(RegistroHora.fecha)).label('dias_trabajados')
        ).join(Empleado, RegistroHora.empleado_id == Empleado.id)

        if proyecto_id:
            query = query.filter(RegistroHora.proyecto_id == proyecto_id)

        if fecha_desde:
            query = query.filter(RegistroHora.fecha >= fecha_desde)

        if fecha_hasta:
            query = query.filter(RegistroHora.fecha <= fecha_hasta)

        resultados = query.group_by(
            RegistroHora.empleado_id,
            Empleado.nombre,
            Empleado.apellido,
            Empleado.tarifa_hora
        ).all()

        resumenes = []
        for emp_id, nombre, apellido, tarifa, total_horas, dias in resultados:
            # Calcular horas extras
            registros_emp = self.db.query(RegistroHora).filter(
                RegistroHora.empleado_id == emp_id
            )
            if proyecto_id:
                registros_emp = registros_emp.filter(RegistroHora.proyecto_id == proyecto_id)
            if fecha_desde:
                registros_emp = registros_emp.filter(RegistroHora.fecha >= fecha_desde)
            if fecha_hasta:
                registros_emp = registros_emp.filter(RegistroHora.fecha <= fecha_hasta)

            horas_extras = sum(
                float(r.horas) - 8.0 for r in registros_emp.all() if float(r.horas) > 8.0
            )

            costo_total = Decimal(total_horas) * Decimal(tarifa) if tarifa else None

            resumenes.append({
                "empleado_id": emp_id,
                "empleado_nombre": f"{nombre} {apellido}",
                "total_horas": Decimal(total_horas),
                "total_horas_extras": Decimal(str(horas_extras)),
                "dias_trabajados": dias,
                "tarifa_hora": Decimal(tarifa) if tarifa else None,
                "costo_total": costo_total
            })

        return resumenes

    def get_resumen_por_proyecto(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[dict]:
        """Obtiene resumen de horas por proyecto"""
        from app.modules.proyectos.models import Proyecto

        query = self.db.query(
            RegistroHora.proyecto_id,
            Proyecto.nombre,
            func.sum(RegistroHora.horas).label('total_horas'),
            func.count(func.distinct(RegistroHora.empleado_id)).label('cantidad_empleados')
        ).join(Proyecto, RegistroHora.proyecto_id == Proyecto.id)

        if fecha_desde:
            query = query.filter(RegistroHora.fecha >= fecha_desde)

        if fecha_hasta:
            query = query.filter(RegistroHora.fecha <= fecha_hasta)

        resultados = query.group_by(
            RegistroHora.proyecto_id,
            Proyecto.nombre
        ).all()

        resumenes = []
        for proj_id, nombre, total_horas, cant_empleados in resultados:
            # Calcular horas extras
            registros_proj = self.db.query(RegistroHora).filter(
                RegistroHora.proyecto_id == proj_id
            )
            if fecha_desde:
                registros_proj = registros_proj.filter(RegistroHora.fecha >= fecha_desde)
            if fecha_hasta:
                registros_proj = registros_proj.filter(RegistroHora.fecha <= fecha_hasta)

            horas_extras = sum(
                float(r.horas) - 8.0 for r in registros_proj.all() if float(r.horas) > 8.0
            )

            resumenes.append({
                "proyecto_id": proj_id,
                "proyecto_nombre": nombre,
                "total_horas": Decimal(total_horas),
                "total_horas_extras": Decimal(str(horas_extras)),
                "cantidad_empleados": cant_empleados,
                "costo_mano_obra": None  # Se calculará en el servicio
            })

        return resumenes
