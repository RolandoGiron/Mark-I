"""
Servicios de lógica de negocio para el módulo Costos.
"""

from typing import List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from app.modules.costos.models import Costo, CategoriaGasto, MetodoCaptura
from app.modules.costos.schemas import (
    CostoCreate,
    CostoUpdate,
    CostoResponse,
    CostoValidarRequest,
    EstadisticasCostos,
    CalcularManoObraRequest,
    CalcularManoObraResponse,
    ManoObraCalculoDetalle
)
from app.modules.costos.repository import CostoRepository
from app.modules.proyectos.repository import ProyectoRepository
from app.modules.horas.repository import RegistroHoraRepository


class CostoService:
    """Servicio para lógica de negocio de Costos"""

    def __init__(self, db: Session):
        self.repository = CostoRepository(db)
        self.proyecto_repository = ProyectoRepository(db)
        self.horas_repository = RegistroHoraRepository(db)
        self.db = db

    def get_costo_by_id(self, costo_id: str) -> CostoResponse:
        """Obtiene un costo por ID"""
        costo = self.repository.get_by_id(costo_id)

        if not costo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Costo con ID {costo_id} no encontrado"
            )

        return self._to_response(costo)

    def get_costos(
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
    ) -> Tuple[List[CostoResponse], int, Decimal]:
        """Obtiene lista de costos con filtros"""
        costos, total, total_monto = self.repository.get_all(
            skip=skip,
            limit=limit,
            proyecto_id=proyecto_id,
            categoria=categoria,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            validado=validado,
            con_factura=con_factura,
            search=search
        )

        return [self._to_response(c) for c in costos], total, total_monto

    def create_costo(self, costo_data: CostoCreate) -> CostoResponse:
        """Crea un nuevo costo"""
        # Verificar que el proyecto existe
        proyecto = self.proyecto_repository.get_by_id(costo_data.proyecto_id)
        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {costo_data.proyecto_id} no encontrado"
            )

        # Validaciones de negocio
        self._validar_costo_data(costo_data, proyecto)

        # Crear costo
        costo = self.repository.create(costo_data)

        return self._to_response(costo)

    def update_costo(self, costo_id: str, costo_data: CostoUpdate) -> CostoResponse:
        """Actualiza un costo existente"""
        costo = self.repository.get_by_id(costo_id)

        if not costo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Costo con ID {costo_id} no encontrado"
            )

        # Actualizar
        costo = self.repository.update(costo, costo_data)

        return self._to_response(costo)

    def delete_costo(self, costo_id: str) -> dict:
        """Elimina un costo"""
        costo = self.repository.get_by_id(costo_id)

        if not costo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Costo con ID {costo_id} no encontrado"
            )

        # Validar que se pueda eliminar
        # TODO: Agregar lógica de permisos cuando exista autenticación

        self.repository.delete(costo)

        return {"message": f"Costo eliminado exitosamente"}

    def upload_factura(
        self,
        costo_id: str,
        file: UploadFile,
        storage_service  # typing circular, se pasa desde route
    ) -> dict:
        """Sube una factura para un costo"""
        costo = self.repository.get_by_id(costo_id)

        if not costo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Costo con ID {costo_id} no encontrado"
            )

        # Validar tipo de archivo
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Permitidos: {allowed_types}"
            )

        # Subir archivo usando storage service
        try:
            factura_url = storage_service.upload_file(
                file=file,
                folder="facturas",
                prefix=f"costo_{costo_id}_"
            )

            # Actualizar costo con URL de factura
            costo = self.repository.update_factura(
                costo,
                factura_url,
                file.filename
            )

            return {
                "id": costo.id,
                "factura_url": factura_url,
                "factura_filename": file.filename,
                "message": "Factura subida exitosamente"
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir factura: {str(e)}"
            )

    def validar_costo(
        self,
        costo_id: str,
        validacion_data: CostoValidarRequest,
        usuario_id: str = "system"  # TODO: Obtener de auth
    ) -> CostoResponse:
        """Valida o rechaza un costo"""
        costo = self.repository.get_by_id(costo_id)

        if not costo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Costo con ID {costo_id} no encontrado"
            )

        costo = self.repository.validar_costo(
            costo,
            validacion_data.validado,
            usuario_id,
            validacion_data.notas_validacion
        )

        return self._to_response(costo)

    def get_total_por_proyecto(self, proyecto_id: str) -> dict:
        """Obtiene el total gastado en un proyecto"""
        # Verificar que el proyecto existe
        proyecto = self.proyecto_repository.get_by_id(proyecto_id)
        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {proyecto_id} no encontrado"
            )

        total = self.repository.get_total_por_proyecto(proyecto_id)

        return {
            "proyecto_id": proyecto_id,
            "proyecto_codigo": proyecto.codigo,
            "proyecto_nombre": proyecto.nombre,
            "presupuesto_total": float(proyecto.presupuesto_total),
            "total_gastado": float(total),
            "porcentaje_gastado": float((total / proyecto.presupuesto_total) * 100) if proyecto.presupuesto_total > 0 else 0,
            "balance": float(proyecto.presupuesto_total - total),
            "en_alerta": (total / proyecto.presupuesto_total) >= 0.9 if proyecto.presupuesto_total > 0 else False
        }

    def get_estadisticas(self, periodo: str = "todos") -> EstadisticasCostos:
        """Obtiene estadísticas de costos"""
        stats = self.repository.get_estadisticas(periodo)
        total_por_categoria = self.repository.get_total_por_categoria()
        total_por_proyecto = self.repository.count_by_proyecto()

        return EstadisticasCostos(
            total_gastos=stats["total_gastos"],
            total_por_categoria=total_por_categoria,
            total_por_proyecto={k: v["total"] for k, v in total_por_proyecto.items()},
            gastos_sin_validar=stats["gastos_sin_validar"],
            gastos_sin_factura=stats["gastos_sin_factura"],
            periodo=periodo
        )

    def _validar_costo_data(self, costo_data: CostoCreate, proyecto) -> None:
        """Validaciones de negocio adicionales"""
        # Validar que el monto no sea mayor al presupuesto del proyecto
        # (solo advertencia, no bloquear)
        total_proyecto = self.repository.get_total_por_proyecto(proyecto.id)
        if total_proyecto + costo_data.monto > proyecto.presupuesto_total:
            # Por ahora solo log, en producción podría ser una alerta
            print(f"⚠️ ALERTA: El gasto excede el presupuesto del proyecto {proyecto.codigo}")

        # Validar que la fecha del gasto no sea futura
        if costo_data.fecha_gasto > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha del gasto no puede ser futura"
            )

    def calcular_mano_obra(
        self,
        solicitud: CalcularManoObraRequest
    ) -> CalcularManoObraResponse:
        """
        Calcula los costos de mano de obra basándose en registros de horas
        y crea automáticamente un costo en la categoría MANO_OBRA
        """
        # Validar que el proyecto existe
        proyecto = self.proyecto_repository.get_by_id(solicitud.proyecto_id)
        if not proyecto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proyecto con ID {solicitud.proyecto_id} no encontrado"
            )

        # Validar fechas
        if solicitud.fecha_hasta < solicitud.fecha_desde:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de fin no puede ser anterior a la fecha de inicio"
            )

        # Obtener resumen de horas por empleado para el proyecto y periodo
        resumen_empleados = self.horas_repository.get_resumen_por_empleado(
            proyecto_id=solicitud.proyecto_id,
            fecha_desde=solicitud.fecha_desde.date(),
            fecha_hasta=solicitud.fecha_hasta.date()
        )

        if not resumen_empleados:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron registros de horas para el periodo especificado"
            )

        # Calcular el monto total y preparar detalles
        monto_total = Decimal('0')
        total_horas = Decimal('0')
        detalles = []

        for resumen in resumen_empleados:
            if resumen['tarifa_hora'] is None or resumen['tarifa_hora'] == 0:
                # Advertir pero continuar sin ese empleado
                print(f"⚠️ Empleado {resumen['empleado_nombre']} no tiene tarifa configurada")
                continue

            costo_empleado = resumen['costo_total']
            monto_total += costo_empleado
            total_horas += resumen['total_horas']

            detalles.append(ManoObraCalculoDetalle(
                empleado_id=resumen['empleado_id'],
                empleado_nombre=resumen['empleado_nombre'],
                total_horas=resumen['total_horas'],
                tarifa_hora=resumen['tarifa_hora'],
                costo_total=costo_empleado
            ))

        if monto_total == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo calcular el costo. Verifique que los empleados tengan tarifas configuradas."
            )

        # Crear la descripción
        periodo_str = f"{solicitud.fecha_desde.strftime('%d/%m/%Y')} al {solicitud.fecha_hasta.strftime('%d/%m/%Y')}"
        descripcion = solicitud.descripcion or f"Mano de obra del {periodo_str}"

        # Crear el costo automáticamente
        costo_data = CostoCreate(
            proyecto_id=solicitud.proyecto_id,
            categoria=CategoriaGasto.MANO_OBRA,
            monto=monto_total,
            descripcion=descripcion,
            proveedor_nombre=None,
            fecha_gasto=solicitud.fecha_hasta,
            metodo_captura=MetodoCaptura.CALCULO_AUTOMATICO
        )

        costo = self.repository.create(costo_data)

        # Marcar como validado automáticamente
        costo = self.repository.validar_costo(
            costo,
            validado=True,
            usuario_id="system",
            notas=f"Cálculo automático basado en {len(detalles)} empleados, {total_horas} horas totales"
        )

        # Preparar la respuesta
        return CalcularManoObraResponse(
            costo_id=costo.id,
            proyecto_id=solicitud.proyecto_id,
            proyecto_nombre=proyecto.nombre,
            periodo_inicio=solicitud.fecha_desde,
            periodo_fin=solicitud.fecha_hasta,
            total_horas=total_horas,
            monto_total=monto_total,
            cantidad_empleados=len(detalles),
            detalle_empleados=detalles
        )

    def _to_response(self, costo: Costo) -> CostoResponse:
        """Convierte un modelo Costo a CostoResponse"""
        return CostoResponse(
            id=costo.id,
            proyecto_id=costo.proyecto_id,
            proyecto_codigo=costo.proyecto.codigo if costo.proyecto else None,
            proyecto_nombre=costo.proyecto.nombre if costo.proyecto else None,
            categoria=costo.categoria,
            monto=costo.monto,
            descripcion=costo.descripcion,
            proveedor_nombre=costo.proveedor_nombre,
            fecha_gasto=costo.fecha_gasto,
            factura_url=costo.factura_url,
            factura_filename=costo.factura_filename,
            metodo_captura=costo.metodo_captura,
            validado=costo.validado,
            validado_por=costo.validado_por,
            validado_en=costo.validado_en,
            notas_validacion=costo.notas_validacion,
            creado_en=costo.creado_en,
            actualizado_en=costo.actualizado_en,
            dias_desde_gasto=costo.dias_desde_gasto,
            tiene_factura=costo.tiene_factura
        )
