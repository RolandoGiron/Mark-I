"""
Repository de Personal
"""
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.modules.personal.models import Empleado
from app.modules.personal.schemas import EmpleadoCreate, EmpleadoUpdate


class EmpleadoRepository:
    """Repository para operaciones de base de datos de Empleados"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, empleado_id: str) -> Optional[Empleado]:
        """Obtiene un empleado por ID"""
        return self.db.query(Empleado).filter(Empleado.id == empleado_id).first()

    def get_by_documento(self, documento: str) -> Optional[Empleado]:
        """Obtiene un empleado por documento de identidad"""
        return self.db.query(Empleado).filter(Empleado.documento_identidad == documento).first()

    def get_by_usuario_id(self, usuario_id: str) -> Optional[Empleado]:
        """Obtiene un empleado por ID de usuario asociado"""
        return self.db.query(Empleado).filter(Empleado.usuario_id == usuario_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        cargo: Optional[str] = None,
        activo: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[Empleado], int]:
        """
        Obtiene todos los empleados con filtros opcionales

        Args:
            skip: Cantidad de registros a saltar
            limit: Cantidad máxima de registros a retornar
            cargo: Filtrar por cargo
            activo: Filtrar por estado activo
            search: Búsqueda por nombre, apellido o documento

        Returns:
            Tupla con (lista de empleados, total de registros)
        """
        query = self.db.query(Empleado)

        # Aplicar filtros
        if cargo:
            query = query.filter(Empleado.cargo == cargo.lower())

        if activo is not None:
            query = query.filter(Empleado.activo == activo)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Empleado.nombre.ilike(search_pattern)) |
                (Empleado.apellido.ilike(search_pattern)) |
                (Empleado.documento_identidad.ilike(search_pattern))
            )

        # Obtener total
        total = query.count()

        # Aplicar paginación y ordenamiento
        empleados = query.order_by(Empleado.apellido, Empleado.nombre).offset(skip).limit(limit).all()

        return empleados, total

    def create(self, empleado_data: EmpleadoCreate) -> Empleado:
        """Crea un nuevo empleado"""
        empleado = Empleado(**empleado_data.model_dump())
        self.db.add(empleado)
        self.db.commit()
        self.db.refresh(empleado)
        return empleado

    def update(self, empleado: Empleado, empleado_data: EmpleadoUpdate) -> Empleado:
        """Actualiza un empleado existente"""
        update_data = empleado_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(empleado, field, value)

        self.db.commit()
        self.db.refresh(empleado)
        return empleado

    def delete(self, empleado: Empleado) -> bool:
        """Elimina un empleado (soft delete - marca como inactivo)"""
        empleado.activo = False
        self.db.commit()
        return True

    def hard_delete(self, empleado: Empleado) -> bool:
        """Elimina permanentemente un empleado"""
        self.db.delete(empleado)
        self.db.commit()
        return True

    def exists_documento(self, documento: str, exclude_id: Optional[str] = None) -> bool:
        """Verifica si existe un empleado con el documento dado"""
        query = self.db.query(Empleado).filter(Empleado.documento_identidad == documento)

        if exclude_id:
            query = query.filter(Empleado.id != exclude_id)

        return query.first() is not None

    def get_activos(self) -> List[Empleado]:
        """Obtiene todos los empleados activos"""
        return self.db.query(Empleado).filter(Empleado.activo == True).all()

    def get_by_cargo(self, cargo: str) -> List[Empleado]:
        """Obtiene empleados por cargo"""
        return self.db.query(Empleado).filter(
            Empleado.cargo == cargo.lower(),
            Empleado.activo == True
        ).all()

    def get_stats(self) -> dict:
        """Obtiene estadísticas de empleados"""
        total = self.db.query(Empleado).count()
        activos = self.db.query(Empleado).filter(Empleado.activo == True).count()

        # Contar por cargo
        cargos = self.db.query(
            Empleado.cargo,
            func.count(Empleado.id).label('cantidad')
        ).filter(Empleado.activo == True).group_by(Empleado.cargo).all()

        por_cargo = {cargo: cantidad for cargo, cantidad in cargos}

        # Tarifa promedio
        tarifa_avg = self.db.query(func.avg(Empleado.tarifa_hora)).filter(
            Empleado.activo == True
        ).scalar() or 0

        return {
            "total_empleados": total,
            "empleados_activos": activos,
            "empleados_inactivos": total - activos,
            "por_cargo": por_cargo,
            "tarifa_promedio": float(tarifa_avg)
        }
