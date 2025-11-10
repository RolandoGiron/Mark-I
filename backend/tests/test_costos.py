"""
Tests para el módulo de costos/gastos.
"""

import pytest
import io
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.modules.costos.models import Costo, CategoriaGasto, MetodoCaptura
from app.modules.proyectos.models import Proyecto, EstadoProyecto


@pytest.fixture
def proyecto_test(db_session: Session):
    """Crea un proyecto para asociar costos"""
    proyecto = Proyecto(
        codigo="COST-TEST",
        nombre="Proyecto para Costos Test",
        cliente="Cliente Test",
        presupuesto_total=Decimal("100000.00"),
        estado=EstadoProyecto.EN_PROGRESO
    )
    db_session.add(proyecto)
    db_session.commit()
    db_session.refresh(proyecto)
    return proyecto


@pytest.fixture
def costo_data(proyecto_test):
    """Datos de ejemplo para crear un costo"""
    return {
        "proyecto_id": proyecto_test.id,
        "categoria": "materiales",
        "monto": 1500.50,
        "descripcion": "Compra de materiales de construcción",
        "proveedor_nombre": "Proveedor Test",
        "fecha_gasto": datetime.utcnow().isoformat(),
        "metodo_captura": "manual_web"
    }


@pytest.fixture
def costo_existente(db_session: Session, proyecto_test, costo_data):
    """Crea un costo en la BD para tests"""
    costo = Costo(
        proyecto_id=costo_data["proyecto_id"],
        categoria=CategoriaGasto.MATERIALES,
        monto=Decimal(str(costo_data["monto"])),
        descripcion=costo_data["descripcion"],
        proveedor_nombre=costo_data["proveedor_nombre"],
        fecha_gasto=datetime.fromisoformat(costo_data["fecha_gasto"]),
        metodo_captura=MetodoCaptura.MANUAL_WEB,
        validado=False
    )
    db_session.add(costo)
    db_session.commit()
    db_session.refresh(costo)
    return costo


@pytest.mark.costos
class TestCostosCRUD:
    """Tests para operaciones CRUD de costos"""

    def test_create_costo_success(self, client: TestClient, costo_data):
        """Test crear costo exitosamente"""
        response = client.post("/api/v1/costos", json=costo_data)

        assert response.status_code == 201
        data = response.json()
        assert data["proyecto_id"] == costo_data["proyecto_id"]
        assert data["categoria"] == costo_data["categoria"]
        assert float(data["monto"]) == costo_data["monto"]
        assert data["descripcion"] == costo_data["descripcion"]
        assert "id" in data
        assert data["validado"] is False

    def test_create_costo_proyecto_inexistente(self, client: TestClient, costo_data):
        """Test crear costo con proyecto inexistente"""
        costo_data["proyecto_id"] = "99999999-9999-9999-9999-999999999999"

        response = client.post("/api/v1/costos", json=costo_data)

        assert response.status_code == 404

    def test_create_costo_monto_negativo(self, client: TestClient, costo_data):
        """Test crear costo con monto negativo"""
        costo_data["monto"] = -100

        response = client.post("/api/v1/costos", json=costo_data)

        assert response.status_code == 422

    def test_create_costo_monto_excesivo(self, client: TestClient, costo_data):
        """Test crear costo con monto excesivo"""
        costo_data["monto"] = 99999999999

        response = client.post("/api/v1/costos", json=costo_data)

        assert response.status_code == 422

    def test_list_costos(self, client: TestClient, costo_existente):
        """Test listar costos"""
        response = client.get("/api/v1/costos")

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "total_monto" in data
        assert "items" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_list_costos_filter_by_proyecto(self, client: TestClient, costo_existente, proyecto_test):
        """Test listar costos filtrados por proyecto"""
        response = client.get(f"/api/v1/costos?proyecto_id={proyecto_test.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        for costo in data["items"]:
            assert costo["proyecto_id"] == proyecto_test.id

    def test_list_costos_filter_by_categoria(self, client: TestClient, costo_existente):
        """Test listar costos filtrados por categoría"""
        response = client.get("/api/v1/costos?categoria=materiales")

        assert response.status_code == 200
        data = response.json()
        for costo in data["items"]:
            assert costo["categoria"] == "materiales"

    def test_list_costos_filter_by_validado(self, client: TestClient, costo_existente):
        """Test listar costos filtrados por validación"""
        response = client.get("/api/v1/costos?validado=false")

        assert response.status_code == 200
        data = response.json()
        for costo in data["items"]:
            assert costo["validado"] is False

    def test_list_costos_filter_by_fecha(self, client: TestClient, costo_existente):
        """Test listar costos filtrados por rango de fechas"""
        fecha_desde = (datetime.utcnow() - timedelta(days=1)).isoformat()
        fecha_hasta = (datetime.utcnow() + timedelta(days=1)).isoformat()

        response = client.get(
            f"/api/v1/costos?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_list_costos_search(self, client: TestClient, costo_existente):
        """Test buscar costos"""
        response = client.get("/api/v1/costos?search=materiales")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_get_costo_by_id(self, client: TestClient, costo_existente):
        """Test obtener costo por ID"""
        response = client.get(f"/api/v1/costos/{costo_existente.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == costo_existente.id
        assert float(data["monto"]) == float(costo_existente.monto)

    def test_get_costo_by_id_not_found(self, client: TestClient):
        """Test obtener costo inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        response = client.get(f"/api/v1/costos/{fake_id}")

        assert response.status_code == 404

    def test_update_costo_success(self, client: TestClient, costo_existente):
        """Test actualizar costo exitosamente"""
        update_data = {
            "descripcion": "Descripción actualizada",
            "monto": 2000.00,
            "categoria": "herramientas"
        }

        response = client.put(
            f"/api/v1/costos/{costo_existente.id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["descripcion"] == "Descripción actualizada"
        assert float(data["monto"]) == 2000.00
        assert data["categoria"] == "herramientas"

    def test_update_costo_not_found(self, client: TestClient):
        """Test actualizar costo inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        update_data = {"descripcion": "Test"}

        response = client.put(f"/api/v1/costos/{fake_id}", json=update_data)

        assert response.status_code == 404

    def test_delete_costo_success(self, client: TestClient, costo_existente):
        """Test eliminar costo exitosamente"""
        response = client.delete(f"/api/v1/costos/{costo_existente.id}")

        assert response.status_code == 200

        # Verificar que no existe
        get_response = client.get(f"/api/v1/costos/{costo_existente.id}")
        assert get_response.status_code == 404

    def test_delete_costo_not_found(self, client: TestClient):
        """Test eliminar costo inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        response = client.delete(f"/api/v1/costos/{fake_id}")

        assert response.status_code == 404


@pytest.mark.costos
class TestCostosFacturas:
    """Tests para funcionalidad de facturas"""

    @pytest.mark.skip(reason="Requiere configuración de storage")
    def test_upload_factura_jpg(self, client: TestClient, costo_existente):
        """Test subir factura JPG"""
        # Crear un archivo de imagen simulado
        file_content = b"fake image content"
        files = {"file": ("factura.jpg", io.BytesIO(file_content), "image/jpeg")}

        response = client.post(
            f"/api/v1/costos/{costo_existente.id}/factura",
            files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert "factura_url" in data
        assert "factura_filename" in data
        assert "message" in data

    @pytest.mark.skip(reason="Requiere configuración de storage")
    def test_upload_factura_png(self, client: TestClient, costo_existente):
        """Test subir factura PNG"""
        file_content = b"fake png content"
        files = {"file": ("factura.png", io.BytesIO(file_content), "image/png")}

        response = client.post(
            f"/api/v1/costos/{costo_existente.id}/factura",
            files=files
        )

        assert response.status_code == 200

    @pytest.mark.skip(reason="Requiere configuración de storage")
    def test_upload_factura_pdf(self, client: TestClient, costo_existente):
        """Test subir factura PDF"""
        file_content = b"%PDF-1.4 fake pdf content"
        files = {"file": ("factura.pdf", io.BytesIO(file_content), "application/pdf")}

        response = client.post(
            f"/api/v1/costos/{costo_existente.id}/factura",
            files=files
        )

        assert response.status_code == 200

    def test_upload_factura_costo_not_found(self, client: TestClient):
        """Test subir factura a costo inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        file_content = b"fake image"
        files = {"file": ("factura.jpg", io.BytesIO(file_content), "image/jpeg")}

        response = client.post(f"/api/v1/costos/{fake_id}/factura", files=files)

        assert response.status_code == 404

    def test_list_costos_con_factura(self, client: TestClient, costo_existente):
        """Test filtrar costos con factura"""
        # Primero subir una factura
        file_content = b"fake image"
        files = {"file": ("factura.jpg", io.BytesIO(file_content), "image/jpeg")}
        client.post(f"/api/v1/costos/{costo_existente.id}/factura", files=files)

        # Ahora filtrar
        response = client.get("/api/v1/costos?con_factura=true")

        assert response.status_code == 200
        data = response.json()
        for costo in data["items"]:
            assert costo["tiene_factura"] is True


@pytest.mark.costos
class TestCostosValidacion:
    """Tests para funcionalidad de validación"""

    def test_validar_costo_success(self, client: TestClient, costo_existente):
        """Test validar costo exitosamente"""
        validacion_data = {
            "validado": True,
            "notas_validacion": "Factura verificada y aprobada"
        }

        response = client.post(
            f"/api/v1/costos/{costo_existente.id}/validar",
            json=validacion_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["validado"] is True
        assert data["notas_validacion"] == "Factura verificada y aprobada"
        assert data["validado_en"] is not None

    def test_rechazar_costo(self, client: TestClient, costo_existente):
        """Test rechazar costo"""
        validacion_data = {
            "validado": False,
            "notas_validacion": "Factura rechazada - monto incorrecto"
        }

        response = client.post(
            f"/api/v1/costos/{costo_existente.id}/validar",
            json=validacion_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["validado"] is False

    def test_validar_costo_not_found(self, client: TestClient):
        """Test validar costo inexistente"""
        fake_id = "99999999-9999-9999-9999-999999999999"
        validacion_data = {"validado": True}

        response = client.post(f"/api/v1/costos/{fake_id}/validar", json=validacion_data)

        assert response.status_code == 404


@pytest.mark.costos
class TestCostosEstadisticas:
    """Tests para endpoints de estadísticas"""

    def test_get_total_por_proyecto(self, client: TestClient, costo_existente, proyecto_test):
        """Test obtener total gastado en proyecto"""
        response = client.get(f"/api/v1/costos/proyecto/{proyecto_test.id}/total")

        assert response.status_code == 200
        data = response.json()
        assert "total_gastado" in data
        assert "presupuesto_total" in data
        assert "porcentaje_gastado" in data

    def test_get_estadisticas_generales(self, client: TestClient, costo_existente):
        """Test obtener estadísticas generales"""
        response = client.get("/api/v1/costos/stats/general")

        assert response.status_code == 200
        data = response.json()
        assert "total_gastos" in data
        assert "total_por_categoria" in data
        assert "gastos_sin_validar" in data
        assert "gastos_sin_factura" in data

    def test_get_estadisticas_por_periodo(self, client: TestClient, costo_existente):
        """Test obtener estadísticas por periodo"""
        periodos = ["hoy", "semana", "mes", "año", "todos"]

        for periodo in periodos:
            response = client.get(f"/api/v1/costos/stats/general?periodo={periodo}")

            assert response.status_code == 200
            data = response.json()
            assert data["periodo"] == periodo


@pytest.mark.costos
@pytest.mark.integration
class TestCostosIntegration:
    """Tests de integración para costos"""

    @pytest.mark.skip(reason="Requiere configuración de storage")
    def test_create_upload_validate_workflow(
        self, client: TestClient, costo_data
    ):
        """Test flujo completo: crear, subir factura y validar"""
        # 1. Crear costo
        create_response = client.post("/api/v1/costos", json=costo_data)
        assert create_response.status_code == 201
        costo_id = create_response.json()["id"]

        # 2. Subir factura
        file_content = b"fake invoice image"
        files = {"file": ("factura.jpg", io.BytesIO(file_content), "image/jpeg")}
        upload_response = client.post(
            f"/api/v1/costos/{costo_id}/factura",
            files=files
        )
        assert upload_response.status_code == 200

        # 3. Validar
        validacion_data = {"validado": True, "notas_validacion": "Todo correcto"}
        validar_response = client.post(
            f"/api/v1/costos/{costo_id}/validar",
            json=validacion_data
        )
        assert validar_response.status_code == 200
        assert validar_response.json()["validado"] is True

    def test_categorias_de_gasto(self, client: TestClient, proyecto_test):
        """Test todas las categorías de gasto"""
        categorias = [
            "materiales", "mano_obra", "transporte", "herramientas",
            "subcontrato", "permisos", "servicios", "otros"
        ]

        for categoria in categorias:
            data = {
                "proyecto_id": proyecto_test.id,
                "categoria": categoria,
                "monto": 1000.00,
                "descripcion": f"Gasto de {categoria}",
                "fecha_gasto": datetime.utcnow().isoformat(),
                "metodo_captura": "manual_web"
            }

            response = client.post("/api/v1/costos", json=data)
            assert response.status_code == 201
            assert response.json()["categoria"] == categoria

    def test_metodos_de_captura(self, client: TestClient, proyecto_test):
        """Test todos los métodos de captura"""
        metodos = ["manual_web", "manual_bot", "foto_bot", "ocr_auto", "voz", "api"]

        for i, metodo in enumerate(metodos):
            data = {
                "proyecto_id": proyecto_test.id,
                "categoria": "materiales",
                "monto": 500.00 + i,
                "descripcion": f"Capturado por {metodo}",
                "fecha_gasto": datetime.utcnow().isoformat(),
                "metodo_captura": metodo
            }

            response = client.post("/api/v1/costos", json=data)
            assert response.status_code == 201
            assert response.json()["metodo_captura"] == metodo
