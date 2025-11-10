"""
Repository de Notificaciones
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.modules.notificaciones.models import Notificacion
from app.modules.notificaciones.schemas import NotificacionCreate, NotificacionUpdate


class NotificacionRepository:
    """Repository para operaciones de base de datos de Notificaciones"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, notificacion_id: str) -> Optional[Notificacion]:
        """Obtiene una notificación por ID"""
        return self.db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        usuario_id: Optional[str] = None,
        tipo: Optional[str] = None,
        leida: Optional[bool] = None
    ) -> tuple[List[Notificacion], int]:
        """
        Obtiene todas las notificaciones con filtros opcionales

        Args:
            skip: Cantidad de registros a saltar
            limit: Cantidad máxima de registros a retornar
            usuario_id: Filtrar por usuario
            tipo: Filtrar por tipo
            leida: Filtrar por estado de lectura

        Returns:
            Tupla con (lista de notificaciones, total de registros)
        """
        query = self.db.query(Notificacion)

        # Aplicar filtros
        if usuario_id:
            query = query.filter(Notificacion.usuario_id == usuario_id)

        if tipo:
            query = query.filter(Notificacion.tipo == tipo.lower())

        if leida is not None:
            query = query.filter(Notificacion.leida == leida)

        # Obtener total
        total = query.count()

        # Aplicar paginación y ordenamiento (más recientes primero)
        notificaciones = query.order_by(Notificacion.creado_en.desc()).offset(skip).limit(limit).all()

        return notificaciones, total

    def create(self, notificacion_data: NotificacionCreate) -> Notificacion:
        """Crea una nueva notificación"""
        notificacion = Notificacion(**notificacion_data.model_dump())
        self.db.add(notificacion)
        self.db.commit()
        self.db.refresh(notificacion)
        return notificacion

    def update(self, notificacion: Notificacion, notificacion_data: NotificacionUpdate) -> Notificacion:
        """Actualiza una notificación"""
        notificacion.leida = notificacion_data.leida

        if notificacion_data.leida and not notificacion.leida_en:
            notificacion.leida_en = datetime.utcnow()
        elif not notificacion_data.leida:
            notificacion.leida_en = None

        self.db.commit()
        self.db.refresh(notificacion)
        return notificacion

    def marcar_como_leida(self, notificacion: Notificacion) -> Notificacion:
        """Marca una notificación como leída"""
        notificacion.leida = True
        notificacion.leida_en = datetime.utcnow()
        self.db.commit()
        self.db.refresh(notificacion)
        return notificacion

    def marcar_todas_leidas(self, usuario_id: str) -> int:
        """Marca todas las notificaciones de un usuario como leídas"""
        count = self.db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.leida == False
        ).update(
            {
                "leida": True,
                "leida_en": datetime.utcnow()
            },
            synchronize_session=False
        )
        self.db.commit()
        return count

    def delete(self, notificacion: Notificacion) -> bool:
        """Elimina una notificación"""
        self.db.delete(notificacion)
        self.db.commit()
        return True

    def delete_antiguas(self, dias: int = 30) -> int:
        """Elimina notificaciones antiguas (más de X días)"""
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        count = self.db.query(Notificacion).filter(
            Notificacion.creado_en < fecha_limite,
            Notificacion.leida == True  # Solo eliminar las ya leídas
        ).delete(synchronize_session=False)
        self.db.commit()
        return count

    def count_no_leidas(self, usuario_id: str) -> int:
        """Cuenta las notificaciones no leídas de un usuario"""
        return self.db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.leida == False
        ).count()

    def get_recientes(self, usuario_id: str, horas: int = 24) -> List[Notificacion]:
        """Obtiene las notificaciones recientes (últimas X horas)"""
        fecha_limite = datetime.utcnow() - timedelta(hours=horas)
        return self.db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.creado_en >= fecha_limite
        ).order_by(Notificacion.creado_en.desc()).all()

    def get_stats(self, usuario_id: str) -> dict:
        """Obtiene estadísticas de notificaciones de un usuario"""
        total = self.db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id
        ).count()

        no_leidas = self.count_no_leidas(usuario_id)

        # Contar por tipo
        tipos = self.db.query(
            Notificacion.tipo,
            func.count(Notificacion.id).label('cantidad')
        ).filter(
            Notificacion.usuario_id == usuario_id
        ).group_by(Notificacion.tipo).all()

        por_tipo = {tipo: cantidad for tipo, cantidad in tipos}

        # Notificaciones recientes (24h)
        fecha_limite = datetime.utcnow() - timedelta(hours=24)
        recientes_24h = self.db.query(Notificacion).filter(
            Notificacion.usuario_id == usuario_id,
            Notificacion.creado_en >= fecha_limite
        ).count()

        return {
            "total_notificaciones": total,
            "no_leidas": no_leidas,
            "leidas": total - no_leidas,
            "por_tipo": por_tipo,
            "recientes_24h": recientes_24h
        }
