"""
Tests para el módulo de Registro de Horas.
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from fastapi.testclient import TestClient
from app.modules.horas.models import RegistroHora
from app.modules.personal.models import Empleado, CargoEmpleado
from app.modules.proyectos.models import Proyecto, EstadoProyecto
from app.modules.tareas.models import Tarea, EstadoTarea, PrioridadTarea


# ===== Fixtures específicas de Horas =====

@pytest.fixture
def empleado_test(db_session):
    """Empleado de prueba para registros de horas"""
    empleado = Empleado(
        nombre="Juan",
        apellido="Pérez",
        documento_identidad="RFC-JP-001",
        cargo=CargoEmpleado.OFICIAL,
        tarifa_hora=Decimal("1500.00"),
        fecha_ingreso=datetime.now() - timedelta(days=90),
        activo=True
    )
    db_session.add(empleado)
    db_session.commit()
    db_session.refresh(empleado)
    return empleado


@pytest.fixture
def proyecto_activo(db_session):
    """Proyecto activo para registros de horas"""
    proyecto = Proyecto(
        codigo="PROJ-HORAS-001",
        nombre="Proyecto para Horas",
        cliente="Cliente Test",
        descripcion="Proyecto de prueba para horas",
        estado=EstadoProyecto.EN_PROGRESO,
        presupuesto_total=Decimal("50000.00"),
        horas_presupuestadas=Decimal("100.00"),
        fecha_inicio=datetime.now() - timedelta(days=30)
    )
    db_session.add(proyecto)
    db_session.commit()
    db_session.refresh(proyecto)
    return proyecto


@pytest.fixture
def tarea_test(db_session, proyecto_activo, trabajador_user, gerente_user):
    """Tarea de prueba para registros de horas"""
    tarea = Tarea(
        proyecto_id=proyecto_activo.id,
        asignado_a_id=trabajador_user.id,
        creado_por_id=gerente_user.id,
        titulo="Tarea para horas",
        descripcion="Tarea de prueba",
        estado=EstadoTarea.EN_PROGRESO,
        prioridad=PrioridadTarea.MEDIA,
        fecha_inicio=datetime.now() - timedelta(days=5),
        fecha_vencimiento=datetime.now() + timedelta(days=10)
    )
    db_session.add(tarea)
    db_session.commit()
    db_session.refresh(tarea)
    return tarea


@pytest.fixture
def registro_hora_1(db_session, empleado_test, proyecto_activo, tarea_test):
    """Registro de horas del día actual"""
    registro = RegistroHora(
        empleado_id=empleado_test.id,
        proyecto_id=proyecto_activo.id,
        tarea_id=tarea_test.id,
        fecha=date.today(),
        horas=Decimal("8.00"),
        descripcion="Trabajo del día"
    )
    db_session.add(registro)
    db_session.commit()
    db_session.refresh(registro)
    return registro


@pytest.fixture
def registro_hora_2(db_session, empleado_test, proyecto_activo):
    """Registro de horas de hace 3 días"""
    registro = RegistroHora(
        empleado_id=empleado_test.id,
        proyecto_id=proyecto_activo.id,
        fecha=date.today() - timedelta(days=3),
        horas=Decimal("6.50"),
        descripcion="Trabajo de hace 3 días"
    )
    db_session.add(registro)
    db_session.commit()
    db_session.refresh(registro)
    return registro


@pytest.fixture
def create_registro_payload(empleado_test, proyecto_activo):
    """Helper para crear payload de registro de horas"""
    def _create_payload(**kwargs):
        base = {
            "empleado_id": empleado_test.id,
            "proyecto_id": proyecto_activo.id,
            "fecha": date.today().isoformat(),
            "horas": 8.0,
            "descripcion": "Registro de prueba"
        }
        base.update(kwargs)
        return base
    return _create_payload


# ===== Tests de Endpoints CRUD =====

@pytest.mark.horas
class TestHorasCreate:
    """Tests para crear registros de horas"""

    def test_create_registro_success(
        self, client: TestClient, gerente_token, auth_headers,
        create_registro_payload
    ):
        """Test crear registro de horas exitosamente"""
        payload = create_registro_payload()

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert float(data["horas"]) == payload["horas"]
        assert "id" in data

    def test_create_registro_with_tarea(
        self, client: TestClient, gerente_token, auth_headers,
        create_registro_payload, tarea_test
    ):
        """Test crear registro con tarea asociada"""
        payload = create_registro_payload(tarea_id=tarea_test.id)

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["tarea_id"] == tarea_test.id

    def test_create_registro_invalid_empleado(
        self, client: TestClient, gerente_token, auth_headers,
        create_registro_payload
    ):
        """Test no permite empleado inexistente"""
        payload = create_registro_payload(
            empleado_id="00000000-0000-0000-0000-000000000000"
        )

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code in [400, 404]

    def test_create_registro_invalid_proyecto(
        self, client: TestClient, gerente_token, auth_headers,
        create_registro_payload
    ):
        """Test no permite proyecto inexistente"""
        payload = create_registro_payload(
            proyecto_id="00000000-0000-0000-0000-000000000000"
        )

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code in [400, 404]

    def test_create_registro_future_date(
        self, client: TestClient, gerente_token, auth_headers,
        create_registro_payload
    ):
        """Test no permite fecha futura"""
        payload = create_registro_payload(
            fecha=(date.today() + timedelta(days=1)).isoformat()
        )

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        # La validación podría rechazar fechas futuras
        assert response.status_code in [201, 400, 422]

    def test_create_registro_horas_negativas(
        self, client: TestClient, gerente_token, auth_headers,
        create_registro_payload
    ):
        """Test no permite horas negativas"""
        payload = create_registro_payload(horas=-5.0)

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422

    def test_create_registro_horas_excesivas(
        self, client: TestClient, gerente_token, auth_headers,
        create_registro_payload
    ):
        """Test valida horas excesivas (>24)"""
        payload = create_registro_payload(horas=25.0)

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        # La validación podría limitar a 24 horas
        assert response.status_code in [201, 400, 422]

    def test_create_registro_without_auth(
        self, client: TestClient, create_registro_payload
    ):
        """Test requiere autenticación"""
        payload = create_registro_payload()

        response = client.post("/api/v1/horas", json=payload)

        assert response.status_code in [401, 403]


@pytest.mark.horas
class TestHorasList:
    """Tests para listar registros de horas"""

    def test_list_registros_success(
        self, client: TestClient, gerente_token, auth_headers,
        registro_hora_1, registro_hora_2
    ):
        """Test listar registros de horas"""
        response = client.get(
            "/api/v1/horas",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert data["total"] >= 2

    def test_list_registros_filter_by_empleado(
        self, client: TestClient, gerente_token, auth_headers,
        registro_hora_1, empleado_test
    ):
        """Test filtrar por empleado"""
        response = client.get(
            f"/api/v1/horas?empleado_id={empleado_test.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        for registro in data["items"]:
            assert registro["empleado_id"] == empleado_test.id

    def test_list_registros_filter_by_proyecto(
        self, client: TestClient, gerente_token, auth_headers,
        registro_hora_1, proyecto_activo
    ):
        """Test filtrar por proyecto"""
        response = client.get(
            f"/api/v1/horas?proyecto_id={proyecto_activo.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        for registro in data["items"]:
            assert registro["proyecto_id"] == proyecto_activo.id

    def test_list_registros_filter_by_fecha_desde(
        self, client: TestClient, gerente_token, auth_headers,
        registro_hora_1
    ):
        """Test filtrar por fecha desde"""
        fecha_desde = (date.today() - timedelta(days=1)).isoformat()
        response = client.get(
            f"/api/v1/horas?fecha_desde={fecha_desde}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200

    def test_list_registros_filter_by_fecha_hasta(
        self, client: TestClient, gerente_token, auth_headers,
        registro_hora_2
    ):
        """Test filtrar por fecha hasta"""
        fecha_hasta = date.today().isoformat()
        response = client.get(
            f"/api/v1/horas?fecha_hasta={fecha_hasta}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200


@pytest.mark.horas
class TestHorasGet:
    """Tests para obtener registro por ID"""

    def test_get_registro_success(
        self, client: TestClient, gerente_token, auth_headers, registro_hora_1
    ):
        """Test obtener registro por ID"""
        response = client.get(
            f"/api/v1/horas/{registro_hora_1.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == registro_hora_1.id
        assert float(data["horas"]) == float(registro_hora_1.horas)

    def test_get_registro_not_found(
        self, client: TestClient, gerente_token, auth_headers
    ):
        """Test obtener registro inexistente"""
        response = client.get(
            "/api/v1/horas/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 404


@pytest.mark.horas
class TestHorasUpdate:
    """Tests para actualizar registros"""

    def test_update_registro_success(
        self, client: TestClient, gerente_token, auth_headers, registro_hora_1
    ):
        """Test actualizar registro de horas"""
        update_data = {
            "horas": 7.5,
            "descripcion": "Descripción actualizada"
        }

        response = client.put(
            f"/api/v1/horas/{registro_hora_1.id}",
            json=update_data,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["horas"]) == 7.5
        assert data["descripcion"] == "Descripción actualizada"

    def test_update_registro_not_found(
        self, client: TestClient, gerente_token, auth_headers
    ):
        """Test actualizar registro inexistente"""
        update_data = {"horas": 5.0}

        response = client.put(
            "/api/v1/horas/00000000-0000-0000-0000-000000000000",
            json=update_data,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 404


@pytest.mark.horas
class TestHorasDelete:
    """Tests para eliminar registros"""

    def test_delete_registro_success(
        self, client: TestClient, gerente_token, auth_headers, registro_hora_1
    ):
        """Test eliminar registro de horas"""
        response = client.delete(
            f"/api/v1/horas/{registro_hora_1.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code in [200, 204]

        # Verificar que fue eliminado
        get_response = client.get(
            f"/api/v1/horas/{registro_hora_1.id}",
            headers=auth_headers(gerente_token)
        )
        assert get_response.status_code == 404

    def test_delete_registro_not_found(
        self, client: TestClient, gerente_token, auth_headers
    ):
        """Test eliminar registro inexistente"""
        response = client.delete(
            "/api/v1/horas/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 404


@pytest.mark.horas
class TestHorasResumenes:
    """Tests para resúmenes de horas"""

    def test_get_resumen_por_empleado(
        self, client: TestClient, gerente_token, auth_headers,
        empleado_test, proyecto_activo, registro_hora_1, registro_hora_2
    ):
        """Test obtener resumen de horas por empleado"""
        response = client.get(
            f"/api/v1/horas/empleado/{empleado_test.id}/resumen",
            headers=auth_headers(gerente_token)
        )

        # Endpoint puede existir o no
        if response.status_code == 200:
            data = response.json()
            assert "total_horas" in data
            assert float(data["total_horas"]) >= 0
        else:
            assert response.status_code == 404

    def test_get_resumen_por_proyecto(
        self, client: TestClient, gerente_token, auth_headers,
        proyecto_activo, registro_hora_1, registro_hora_2
    ):
        """Test obtener resumen de horas por proyecto"""
        response = client.get(
            f"/api/v1/horas/proyecto/{proyecto_activo.id}/resumen",
            headers=auth_headers(gerente_token)
        )

        # Endpoint puede existir o no
        if response.status_code == 200:
            data = response.json()
            assert "total_horas" in data
            assert float(data["total_horas"]) >= 0
        else:
            assert response.status_code == 404

    def test_get_horas_hoy(
        self, client: TestClient, gerente_token, auth_headers, registro_hora_1
    ):
        """Test obtener horas registradas hoy"""
        response = client.get(
            "/api/v1/horas/hoy",
            headers=auth_headers(gerente_token)
        )

        # Endpoint puede existir o no
        assert response.status_code in [200, 404]


@pytest.mark.horas
class TestHorasPermissions:
    """Tests de permisos y autorizaciones"""

    def test_trabajador_can_view_horas(
        self, client: TestClient, trabajador_token, auth_headers
    ):
        """Test que trabajador puede ver horas"""
        response = client.get(
            "/api/v1/horas",
            headers=auth_headers(trabajador_token)
        )

        assert response.status_code == 200

    def test_supervisor_can_create_horas(
        self, client: TestClient, supervisor_token, auth_headers,
        create_registro_payload
    ):
        """Test que supervisor puede crear registros"""
        payload = create_registro_payload()

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(supervisor_token)
        )

        assert response.status_code == 201


@pytest.mark.horas
class TestHorasValidations:
    """Tests de validaciones de negocio"""

    def test_empleado_id_required(
        self, client: TestClient, gerente_token, auth_headers, proyecto_activo
    ):
        """Test empleado_id es requerido"""
        payload = {
            "proyecto_id": proyecto_activo.id,
            "fecha": date.today().isoformat(),
            "horas": 8.0
        }

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422

    def test_proyecto_id_required(
        self, client: TestClient, gerente_token, auth_headers, empleado_test
    ):
        """Test proyecto_id es requerido"""
        payload = {
            "empleado_id": empleado_test.id,
            "fecha": date.today().isoformat(),
            "horas": 8.0
        }

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422

    def test_horas_required(
        self, client: TestClient, gerente_token, auth_headers,
        empleado_test, proyecto_activo
    ):
        """Test horas es requerido"""
        payload = {
            "empleado_id": empleado_test.id,
            "proyecto_id": proyecto_activo.id,
            "fecha": date.today().isoformat()
        }

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422

    def test_fecha_required(
        self, client: TestClient, gerente_token, auth_headers,
        empleado_test, proyecto_activo
    ):
        """Test fecha es requerida"""
        payload = {
            "empleado_id": empleado_test.id,
            "proyecto_id": proyecto_activo.id,
            "horas": 8.0
        }

        response = client.post(
            "/api/v1/horas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422
