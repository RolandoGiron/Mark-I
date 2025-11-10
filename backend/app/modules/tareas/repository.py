"""
Repository de Tareas
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.modules.tareas.models import Tarea
from app.modules.tareas.schemas import TareaCreate, TareaUpdate


class TareaRepository:
    """Repository para operaciones de base de datos de Tareas"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tarea_id: str) -> Optional[Tarea]:
        """Obtiene una tarea por ID"""
        return self.db.query(Tarea).filter(Tarea.id == tarea_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        proyecto_id: Optional[str] = None,
        asignado_a_id: Optional[str] = None,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Tarea], int]:
        """
        Obtiene todas las tareas con filtros opcionales

        Args:
            skip: Cantidad de registros a saltar
            limit: Cantidad máxima de registros a retornar
            proyecto_id: Filtrar por proyecto
            asignado_a_id: Filtrar por usuario asignado
            estado: Filtrar por estado
            prioridad: Filtrar por prioridad
            search: Búsqueda por título o descripción

        Returns:
            Tupla con (lista de tareas, total de registros)
        """
        query = self.db.query(Tarea)

        # Aplicar filtros
        if proyecto_id:
            query = query.filter(Tarea.proyecto_id == proyecto_id)

        if asignado_a_id:
            query = query.filter(Tarea.asignado_a_id == asignado_a_id)

        if estado:
            query = query.filter(Tarea.estado == estado.lower())

        if prioridad:
            query = query.filter(Tarea.prioridad == prioridad.lower())

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Tarea.titulo.ilike(search_pattern),
                    Tarea.descripcion.ilike(search_pattern)
                )
            )

        # Obtener total
        total = query.count()

        # Aplicar paginación y ordenamiento
        tareas = query.order_by(
            Tarea.fecha_vencimiento.asc().nullslast(),
            Tarea.prioridad.desc(),
            Tarea.creado_en.desc()
        ).offset(skip).limit(limit).all()

        return tareas, total

    def create(self, tarea_data: TareaCreate, creado_por_id: str) -> Tarea:
        """Crea una nueva tarea"""
        tarea_dict = tarea_data.model_dump()
        tarea_dict['creado_por_id'] = creado_por_id

        tarea = Tarea(**tarea_dict)
        self.db.add(tarea)
        self.db.commit()
        self.db.refresh(tarea)
        return tarea

    def update(self, tarea: Tarea, tarea_data: TareaUpdate) -> Tarea:
        """Actualiza una tarea existente"""
        update_data = tarea_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(tarea, field, value)

        self.db.commit()
        self.db.refresh(tarea)
        return tarea

    def delete(self, tarea: Tarea) -> bool:
        """Elimina una tarea"""
        self.db.delete(tarea)
        self.db.commit()
        return True

    def cambiar_estado(self, tarea: Tarea, nuevo_estado: str) -> Tarea:
        """Cambia el estado de una tarea"""
        tarea.estado = nuevo_estado.lower()

        # Si se marca como completada, registrar la fecha
        if nuevo_estado.lower() == 'completada' and not tarea.fecha_completada:
            tarea.fecha_completada = datetime.utcnow()

        # Si se desmarca de completada, limpiar la fecha
        if nuevo_estado.lower() != 'completada' and tarea.fecha_completada:
            tarea.fecha_completada = None

        self.db.commit()
        self.db.refresh(tarea)
        return tarea

    def get_tareas_hoy(self, usuario_id: Optional[str] = None) -> List[Tarea]:
        """Obtiene las tareas que vencen hoy"""
        hoy_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = hoy_inicio + timedelta(days=1)

        query = self.db.query(Tarea).filter(
            Tarea.fecha_vencimiento >= hoy_inicio,
            Tarea.fecha_vencimiento < hoy_fin,
            Tarea.estado.notin_(['completada', 'cancelada'])
        )

        if usuario_id:
            query = query.filter(Tarea.asignado_a_id == usuario_id)

        return query.order_by(Tarea.prioridad.desc()).all()

    def get_tareas_vencidas(self, usuario_id: Optional[str] = None) -> List[Tarea]:
        """Obtiene las tareas vencidas"""
        query = self.db.query(Tarea).filter(
            Tarea.fecha_vencimiento < datetime.utcnow(),
            Tarea.estado.notin_(['completada', 'cancelada'])
        )

        if usuario_id:
            query = query.filter(Tarea.asignado_a_id == usuario_id)

        return query.order_by(Tarea.fecha_vencimiento.asc()).all()

    def get_by_proyecto(self, proyecto_id: str) -> List[Tarea]:
        """Obtiene todas las tareas de un proyecto"""
        return self.db.query(Tarea).filter(Tarea.proyecto_id == proyecto_id).all()

    def get_by_usuario(self, usuario_id: str, solo_activas: bool = True) -> List[Tarea]:
        """Obtiene las tareas asignadas a un usuario"""
        query = self.db.query(Tarea).filter(Tarea.asignado_a_id == usuario_id)

        if solo_activas:
            query = query.filter(Tarea.estado.notin_(['completada', 'cancelada']))

        return query.order_by(Tarea.fecha_vencimiento.asc().nullslast()).all()

    def get_stats(self, proyecto_id: Optional[str] = None) -> dict:
        """Obtiene estadísticas de tareas"""
        query = self.db.query(Tarea)

        if proyecto_id:
            query = query.filter(Tarea.proyecto_id == proyecto_id)

        total = query.count()

        # Contar por estado
        estados = self.db.query(
            Tarea.estado,
            func.count(Tarea.id).label('cantidad')
        )
        if proyecto_id:
            estados = estados.filter(Tarea.proyecto_id == proyecto_id)
        estados = estados.group_by(Tarea.estado).all()
        por_estado = {estado: cantidad for estado, cantidad in estados}

        # Contar por prioridad
        prioridades = self.db.query(
            Tarea.prioridad,
            func.count(Tarea.id).label('cantidad')
        )
        if proyecto_id:
            prioridades = prioridades.filter(Tarea.proyecto_id == proyecto_id)
        prioridades = prioridades.group_by(Tarea.prioridad).all()
        por_prioridad = {prioridad: cantidad for prioridad, cantidad in prioridades}

        # Tareas vencidas
        vencidas_query = self.db.query(Tarea).filter(
            Tarea.fecha_vencimiento < datetime.utcnow(),
            Tarea.estado.notin_(['completada', 'cancelada'])
        )
        if proyecto_id:
            vencidas_query = vencidas_query.filter(Tarea.proyecto_id == proyecto_id)
        tareas_vencidas = vencidas_query.count()

        # Tareas de hoy
        hoy_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = hoy_inicio + timedelta(days=1)
        hoy_query = self.db.query(Tarea).filter(
            Tarea.fecha_vencimiento >= hoy_inicio,
            Tarea.fecha_vencimiento < hoy_fin,
            Tarea.estado.notin_(['completada', 'cancelada'])
        )
        if proyecto_id:
            hoy_query = hoy_query.filter(Tarea.proyecto_id == proyecto_id)
        tareas_hoy = hoy_query.count()

        return {
            "total_tareas": total,
            "por_estado": por_estado,
            "por_prioridad": por_prioridad,
            "tareas_vencidas": tareas_vencidas,
            "tareas_hoy": tareas_hoy
        }
