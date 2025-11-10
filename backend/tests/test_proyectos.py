"""
Tests para el módulo de proyectos.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.proyectos.models import Proyecto, EstadoProyecto


@pytest.fixture
def proyecto_data():
    """Datos de ejemplo para crear un proyecto"""
    return {
        "codigo": "TEST-001",
        "nombre": "Proyecto de Prueba",
        "cliente": "Cliente Test",
        "descripcion": "Descripción del proyecto de prueba",
        "presupuesto_total": 100000.00,
        "horas_presupuestadas": 200.0,
        "fecha_inicio": datetime.utcnow().isoformat(),
        "fecha_fin_estimada": (datetime.utcnow() + timedelta(days=60)).isoformat(),
        "estado": "prospecto",
        "datos_adicionales": {"ubicacion": "Ciudad Test", "tipo": "Residencial"}
    }


@pytest.fixture
def proyecto_existente(db_session: Session, proyecto_data):
    """Crea un proyecto en la BD para tests"""
    proyecto = Proyecto(
        codigo=proyecto_data["codigo"],
        nombre=proyecto_data["nombre"],
        cliente=proyecto_data["cliente"],
        descripcion=proyecto_data["descripcion"],
        presupuesto_total=Decimal(str(proyecto_data["presupuesto_total"])),
        horas_presupuestadas=Decimal(str(proyecto_data["horas_presupuestadas"])),
        fecha_inicio=datetime.fromisoformat(proyecto_data["fecha_inicio"]),
        fecha_fin_estimada=datetime.fromisoformat(proyecto_data["fecha_fin_estimada"]),
        estado=EstadoProyecto.PROSPECTO,
        datos_adicionales=proyecto_data["datos_adicionales"]
    )
    db_session.add(proyecto)
    db_session.commit()
    db_session.refresh(proyecto)
    return proyecto


@pytest.mark.proyectos
class TestProyectosCRUD:
    """Tests para operaciones CRUD de proyectos"""

    def test_create_proyecto_success(self, client: TestClient, proyecto_data):
        """Test crear proyecto exitosamente"""
        response = client.post("/api/v1/proyectos", json=proyecto_data)

        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == proyecto_data["codigo"]
        assert data["nombre"] == proyecto_data["nombre"]
        assert data["cliente"] == proyecto_data["cliente"]
        assert float(data["presupuesto_total"]) == proyecto_data["presupuesto_total"]
        assert "id" in data

    def test_create_proyecto_duplicate_codigo(
        self, client: TestClient, proyecto_data, proyecto_existente
    ):
        """Test crear proyecto con código duplicado"""
        response = client.post("/api/v1/proyectos", json=proyecto_data)

        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        # Verifica que el mensaje mencione el código
        assert ("codigo" in detail or "código" in detail)

    def test_create_proyecto_invalid_presupuesto(self, client: TestClient, proyecto_data):
        """Test crear proyecto con presupuesto inválido"""
        proyecto_data["presupuesto_total"] = -1000

        response = client.post("/api/v1/proyectos", json=proyecto_data)

        assert response.status_code == 422

    def test_create_proyecto_fecha_fin_antes_inicio(self, client: TestClient, proyecto_data):
        """Test crear proyecto con fecha fin antes de inicio"""
        proyecto_data["fecha_fin_estimada"] = (datetime.utcnow() - timedelta(days=10)).isoformat()

        response = client.post("/api/v1/proyectos", json=proyecto_data)

        assert response.status_code == 422

    def test_list_proyectos(self, client: TestClient, proyecto_existente):
        """Test listar proyectos"""
        response = client.get("/api/v1/proyectos")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_list_proyectos_with_pagination(self, client: TestClient, proyecto_existente):
        """Test listar proyectos con paginación"""
        response = client.get("/api/v1/proyectos?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_proyectos_filter_by_estado(self, client: TestClient, proyecto_existente):
        """Test listar proyectos filtrados por estado"""
        response = client.get("/api/v1/proyectos?estado=prospecto")

        assert response.status_code == 200
        data = response.json()
        for proyecto in data["items"]:
            assert proyecto["estado"] == "prospecto"

    def test_list_proyectos_filter_by_cliente(self, client: TestClient, proyecto_existente):
        """Test listar proyectos filtrados por cliente"""
        response = client.get("/api/v1/proyectos?cliente=Cliente%20Test")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_list_proyectos_search(self, client: TestClient, proyecto_existente):
        """Test buscar proyectos"""
        response = client.get("/api/v1/proyectos?search=Prueba")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_get_proyecto_by_id(self, client: TestClient, proyecto_existente):
        """Test obtener proyecto por ID"""
        response = client.get(f"/api/v1/proyectos/{proyecto_existente.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == proyecto_existente.id
        assert data["codigo"] == proyecto_existente.codigo

    def test_get_proyecto_by_id_not_found(self, client: TestClient):
        """Test obtener proyecto inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        response = client.get(f"/api/v1/proyectos/{fake_id}")

        assert response.status_code == 404

    def test_get_proyecto_by_codigo(self, client: TestClient, proyecto_existente):
        """Test obtener proyecto por código"""
        response = client.get(f"/api/v1/proyectos/codigo/{proyecto_existente.codigo}")

        assert response.status_code == 200
        data = response.json()
        assert data["codigo"] == proyecto_existente.codigo
        assert data["nombre"] == proyecto_existente.nombre

    def test_get_proyecto_by_codigo_not_found(self, client: TestClient):
        """Test obtener proyecto por código inexistente"""
        response = client.get("/api/v1/proyectos/codigo/NOEXISTE-999")

        assert response.status_code == 404

    def test_update_proyecto_success(self, client: TestClient, proyecto_existente):
        """Test actualizar proyecto exitosamente"""
        update_data = {
            "nombre": "Nombre Actualizado",
            "estado": "en_progreso",
            "presupuesto_total": 150000.00
        }

        response = client.put(
            f"/api/v1/proyectos/{proyecto_existente.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Nombre Actualizado"
        assert data["estado"] == "en_progreso"
        assert float(data["presupuesto_total"]) == 150000.00

    def test_update_proyecto_not_found(self, client: TestClient):
        """Test actualizar proyecto inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        update_data = {"nombre": "Test"}

        response = client.put(f"/api/v1/proyectos/{fake_id}", json=update_data)

        assert response.status_code == 404

    def test_delete_proyecto_success(self, client: TestClient, proyecto_existente):
        """Test eliminar proyecto exitosamente"""
        response = client.delete(f"/api/v1/proyectos/{proyecto_existente.id}")

        assert response.status_code == 200

        # Verificar que no existe
        get_response = client.get(f"/api/v1/proyectos/{proyecto_existente.id}")
        assert get_response.status_code == 404

    def test_delete_proyecto_not_found(self, client: TestClient):
        """Test eliminar proyecto inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        response = client.delete(f"/api/v1/proyectos/{fake_id}")

        assert response.status_code == 404


@pytest.mark.proyectos
class TestProyectosEstadisticas:
    """Tests para endpoints de estadísticas de proyectos"""

    def test_get_resumen_financiero(self, client: TestClient, proyecto_existente):
        """Test obtener resumen financiero de proyecto"""
        response = client.get(f"/api/v1/proyectos/{proyecto_existente.id}/resumen")

        assert response.status_code == 200
        data = response.json()
        assert "presupuesto_total" in data
        assert "total_gastado" in data
        assert "porcentaje_gastado" in data
        assert "balance" in data
        assert "en_alerta" in data

    def test_get_resumen_financiero_not_found(self, client: TestClient):
        """Test obtener resumen de proyecto inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        response = client.get(f"/api/v1/proyectos/{fake_id}/resumen")

        assert response.status_code == 404

    def test_get_estadisticas_generales(self, client: TestClient, proyecto_existente):
        """Test obtener estadísticas generales"""
        response = client.get("/api/v1/proyectos/stats/general")

        assert response.status_code == 200
        data = response.json()
        # El formato puede variar, acepta ambos
        assert ("total" in data or "total_proyectos" in data)
        if "total" in data:
            assert isinstance(data["total"], int)
            assert data["total"] >= 1
        else:
            assert isinstance(data["total_proyectos"], int)
            assert data["total_proyectos"] >= 1


@pytest.mark.proyectos
@pytest.mark.integration
class TestProyectosIntegration:
    """Tests de integración para proyectos"""

    def test_create_and_update_workflow(self, client: TestClient, proyecto_data):
        """Test flujo completo: crear y actualizar proyecto"""
        # Crear
        create_response = client.post("/api/v1/proyectos", json=proyecto_data)
        assert create_response.status_code == 201
        proyecto_id = create_response.json()["id"]

        # Actualizar a cotización
        update_response = client.put(
            f"/api/v1/proyectos/{proyecto_id}",
            json={"estado": "cotizacion"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["estado"] == "cotizacion"

        # Aprobar
        update_response = client.put(
            f"/api/v1/proyectos/{proyecto_id}",
            json={"estado": "aprobado"}
        )
        assert update_response.status_code == 200

        # Iniciar
        update_response = client.put(
            f"/api/v1/proyectos/{proyecto_id}",
            json={"estado": "en_progreso"}
        )
        assert update_response.status_code == 200

    def test_estados_del_proyecto(self, client: TestClient, proyecto_data):
        """Test todos los estados posibles de un proyecto"""
        estados = ["prospecto", "cotizacion", "aprobado", "en_progreso",
                   "pausado", "completado", "cancelado"]

        for i, estado in enumerate(estados):
            data = proyecto_data.copy()
            data["codigo"] = f"TEST-{i:03d}"
            data["estado"] = estado

            response = client.post("/api/v1/proyectos", json=data)
            assert response.status_code == 201
            assert response.json()["estado"] == estado
