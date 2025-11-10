"""
Repositorio para acceso a datos del módulo Costos.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_

from app.modules.costos.models import Costo, CategoriaGasto
from app.modules.costos.schemas import CostoCreate, CostoUpdate


class CostoRepository:
    """Repositorio para operaciones CRUD de Costos"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, costo_id: str) -> Optional[Costo]:
        """Obtiene un costo por su ID"""
        return (
            self.db.query(Costo)
            .options(joinedload(Costo.proyecto))
            .filter(Costo.id == costo_id)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        proyecto_id: Optional[str] = None,
        categoria: Optional[CategoriaGasto] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        validado: Optional[bool] = None,
        con_factura: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Costo], int, Decimal]:
        """
        Obtiene lista de costos con filtros opcionales.

        Returns:
            tuple: (lista de costos, total de registros, suma total de montos)
        """
        query = self.db.query(Costo).options(joinedload(Costo.proyecto))

        # Filtros
        if proyecto_id:
            query = query.filter(Costo.proyecto_id == proyecto_id)

        if categoria:
            query = query.filter(Costo.categoria == categoria)

        if fecha_desde:
            query = query.filter(Costo.fecha_gasto >= fecha_desde)

        if fecha_hasta:
            query = query.filter(Costo.fecha_gasto <= fecha_hasta)

        if validado is not None:
            query = query.filter(Costo.validado == validado)

        if con_factura is not None:
            if con_factura:
                query = query.filter(Costo.factura_url.isnot(None))
            else:
                query = query.filter(Costo.factura_url.is_(None))

        if search:
            search_filter = or_(
                Costo.descripcion.ilike(f"%{search}%"),
                Costo.proveedor_nombre.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Total de registros
        total = query.count()

        # Suma total de montos (antes de paginación)
        total_monto = query.with_entities(func.sum(Costo.monto)).scalar() or Decimal("0.00")

        # Paginación
        costos = query.order_by(Costo.fecha_gasto.desc()).offset(skip).limit(limit).all()

        return costos, total, total_monto

    def create(self, costo_data: CostoCreate) -> Costo:
        """Crea un nuevo costo"""
        costo = Costo(**costo_data.model_dump())
        self.db.add(costo)
        self.db.commit()
        self.db.refresh(costo)
        return costo

    def update(self, costo: Costo, costo_data: CostoUpdate) -> Costo:
        """Actualiza un costo existente"""
        update_data = costo_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(costo, field, value)

        self.db.commit()
        self.db.refresh(costo)
        return costo

    def delete(self, costo: Costo) -> bool:
        """Elimina un costo"""
        self.db.delete(costo)
        self.db.commit()
        return True

    def update_factura(self, costo: Costo, factura_url: str, factura_filename: str) -> Costo:
        """Actualiza la URL de la factura de un costo"""
        costo.factura_url = factura_url
        costo.factura_filename = factura_filename
        self.db.commit()
        self.db.refresh(costo)
        return costo

    def validar_costo(
        self,
        costo: Costo,
        validado: bool,
        validado_por: str,
        notas: Optional[str] = None
    ) -> Costo:
        """Valida o rechaza un costo"""
        costo.validado = validado
        costo.validado_por = validado_por
        costo.validado_en = datetime.utcnow()
        costo.notas_validacion = notas

        self.db.commit()
        self.db.refresh(costo)
        return costo

    def get_total_por_proyecto(self, proyecto_id: str) -> Decimal:
        """Calcula el total gastado en un proyecto"""
        total = (
            self.db.query(func.sum(Costo.monto))
            .filter(Costo.proyecto_id == proyecto_id)
            .filter(Costo.validado == True)
            .scalar()
        )
        return total or Decimal("0.00")

    def get_total_por_categoria(self, proyecto_id: Optional[str] = None) -> dict:
        """Obtiene el total por categoría"""
        query = self.db.query(
            Costo.categoria,
            func.sum(Costo.monto).label('total')
        )

        if proyecto_id:
            query = query.filter(Costo.proyecto_id == proyecto_id)

        query = query.filter(Costo.validado == True)
        query = query.group_by(Costo.categoria)

        results = query.all()
        return {str(categoria): float(total) for categoria, total in results}

    def get_estadisticas(self, periodo: str = "todos") -> dict:
        """Obtiene estadísticas de costos según periodo"""
        query = self.db.query(Costo)

        # Filtrar por periodo
        if periodo == "hoy":
            query = query.filter(
                func.date(Costo.fecha_gasto) == datetime.utcnow().date()
            )
        elif periodo == "semana":
            fecha_inicio = datetime.utcnow() - timedelta(days=7)
            query = query.filter(Costo.fecha_gasto >= fecha_inicio)
        elif periodo == "mes":
            fecha_inicio = datetime.utcnow() - timedelta(days=30)
            query = query.filter(Costo.fecha_gasto >= fecha_inicio)
        elif periodo == "año":
            fecha_inicio = datetime.utcnow() - timedelta(days=365)
            query = query.filter(Costo.fecha_gasto >= fecha_inicio)

        # Total de gastos
        total_gastos = query.with_entities(func.sum(Costo.monto)).scalar() or Decimal("0.00")

        # Sin validar
        sin_validar = query.filter(Costo.validado == False).count()

        # Sin factura
        sin_factura = query.filter(Costo.factura_url.is_(None)).count()

        return {
            "total_gastos": total_gastos,
            "gastos_sin_validar": sin_validar,
            "gastos_sin_factura": sin_factura
        }

    def count_by_proyecto(self) -> dict:
        """Cuenta y suma gastos por proyecto"""
        from app.modules.proyectos.models import Proyecto

        results = (
            self.db.query(
                Proyecto.codigo,
                func.sum(Costo.monto).label('total'),
                func.count(Costo.id).label('cantidad')
            )
            .join(Proyecto, Costo.proyecto_id == Proyecto.id)
            .filter(Costo.validado == True)
            .group_by(Proyecto.codigo)
            .all()
        )

        return {
            codigo: {"total": float(total), "cantidad": cantidad}
            for codigo, total, cantidad in results
        }
