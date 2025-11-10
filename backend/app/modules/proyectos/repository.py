"""
Repositorio para acceso a datos del módulo Proyectos.
Capa de abstracción entre la base de datos y la lógica de negocio.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.modules.proyectos.models import Proyecto, EstadoProyecto
from app.modules.proyectos.schemas import ProyectoCreate, ProyectoUpdate


class ProyectoRepository:
    """Repositorio para operaciones CRUD de Proyectos"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, proyecto_id: str) -> Optional[Proyecto]:
        """Obtiene un proyecto por su ID"""
        return self.db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()

    def get_by_codigo(self, codigo: str) -> Optional[Proyecto]:
        """Obtiene un proyecto por su código"""
        return self.db.query(Proyecto).filter(Proyecto.codigo == codigo).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        estado: Optional[EstadoProyecto] = None,
        cliente: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Proyecto], int]:
        """
        Obtiene lista de proyectos con filtros opcionales.

        Returns:
            tuple: (lista de proyectos, total de registros)
        """
        query = self.db.query(Proyecto)

        # Filtro por estado
        if estado:
            query = query.filter(Proyecto.estado == estado)

        # Filtro por cliente
        if cliente:
            query = query.filter(Proyecto.cliente.ilike(f"%{cliente}%"))

        # Búsqueda en múltiples campos
        if search:
            search_filter = or_(
                Proyecto.codigo.ilike(f"%{search}%"),
                Proyecto.nombre.ilike(f"%{search}%"),
                Proyecto.cliente.ilike(f"%{search}%"),
                Proyecto.descripcion.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Total antes de paginación
        total = query.count()

        # Paginación
        proyectos = query.order_by(Proyecto.creado_en.desc()).offset(skip).limit(limit).all()

        return proyectos, total

    def create(self, proyecto_data: ProyectoCreate) -> Proyecto:
        """Crea un nuevo proyecto"""
        proyecto = Proyecto(**proyecto_data.model_dump())
        self.db.add(proyecto)
        self.db.commit()
        self.db.refresh(proyecto)
        return proyecto

    def update(self, proyecto: Proyecto, proyecto_data: ProyectoUpdate) -> Proyecto:
        """Actualiza un proyecto existente"""
        update_data = proyecto_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(proyecto, field, value)

        self.db.commit()
        self.db.refresh(proyecto)
        return proyecto

    def delete(self, proyecto: Proyecto) -> bool:
        """Elimina un proyecto"""
        self.db.delete(proyecto)
        self.db.commit()
        return True

    def exists_codigo(self, codigo: str, exclude_id: Optional[str] = None) -> bool:
        """
        Verifica si existe un proyecto con el código dado.

        Args:
            codigo: Código a verificar
            exclude_id: ID de proyecto a excluir (útil para updates)
        """
        query = self.db.query(Proyecto).filter(Proyecto.codigo == codigo)

        if exclude_id:
            query = query.filter(Proyecto.id != exclude_id)

        return query.first() is not None

    def get_by_estado(self, estado: EstadoProyecto) -> List[Proyecto]:
        """Obtiene todos los proyectos con un estado específico"""
        return self.db.query(Proyecto).filter(Proyecto.estado == estado).all()

    def count_by_estado(self) -> dict:
        """Cuenta proyectos por estado"""
        from sqlalchemy import func

        results = (
            self.db.query(Proyecto.estado, func.count(Proyecto.id))
            .group_by(Proyecto.estado)
            .all()
        )

        return {estado: count for estado, count in results}
