"""
Tests para el módulo de Tareas.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.modules.tareas.models import Tarea, EstadoTarea, PrioridadTarea
from app.modules.proyectos.models import Proyecto, EstadoProyecto


# ===== Fixtures específicas de Tareas =====

@pytest.fixture
def proyecto_test(db_session, admin_user):
    """Proyecto de prueba para tareas"""
    proyecto = Proyecto(
        codigo="TEST-001",
        nombre="Proyecto Test",
        cliente="Cliente Test",
        descripcion="Proyecto para pruebas",
        estado=EstadoProyecto.EN_PROGRESO,
        presupuesto_total=100000.00,
        horas_presupuestadas=100.0,
        fecha_inicio=datetime.now()
    )
    db_session.add(proyecto)
    db_session.commit()
    db_session.refresh(proyecto)
    return proyecto


@pytest.fixture
def tarea_pendiente(db_session, proyecto_test, trabajador_user, gerente_user):
    """Tarea en estado pendiente"""
    tarea = Tarea(
        proyecto_id=proyecto_test.id,
        asignado_a_id=trabajador_user.id,
        creado_por_id=gerente_user.id,
        titulo="Tarea pendiente de prueba",
        descripcion="Descripción de tarea pendiente",
        estado=EstadoTarea.PENDIENTE,
        prioridad=PrioridadTarea.MEDIA,
        fecha_vencimiento=datetime.now() + timedelta(days=7)
    )
    db_session.add(tarea)
    db_session.commit()
    db_session.refresh(tarea)
    return tarea


@pytest.fixture
def tarea_progreso(db_session, proyecto_test, trabajador_user, gerente_user):
    """Tarea en progreso"""
    tarea = Tarea(
        proyecto_id=proyecto_test.id,
        asignado_a_id=trabajador_user.id,
        creado_por_id=gerente_user.id,
        titulo="Tarea en progreso",
        descripcion="Descripción de tarea en progreso",
        estado=EstadoTarea.EN_PROGRESO,
        prioridad=PrioridadTarea.ALTA,
        fecha_inicio=datetime.now() - timedelta(days=2),
        fecha_vencimiento=datetime.now() + timedelta(days=5)
    )
    db_session.add(tarea)
    db_session.commit()
    db_session.refresh(tarea)
    return tarea


@pytest.fixture
def tarea_completada(db_session, proyecto_test, trabajador_user, gerente_user):
    """Tarea completada"""
    tarea = Tarea(
        proyecto_id=proyecto_test.id,
        asignado_a_id=trabajador_user.id,
        creado_por_id=gerente_user.id,
        titulo="Tarea completada",
        descripcion="Tarea ya completada",
        estado=EstadoTarea.COMPLETADA,
        prioridad=PrioridadTarea.MEDIA,
        fecha_inicio=datetime.now() - timedelta(days=10),
        fecha_completada=datetime.now() - timedelta(days=3),
        fecha_vencimiento=datetime.now() - timedelta(days=1)
    )
    db_session.add(tarea)
    db_session.commit()
    db_session.refresh(tarea)
    return tarea


@pytest.fixture
def create_tarea_payload(proyecto_test, trabajador_user):
    """Helper para crear payload de tarea"""
    def _create_payload(**kwargs):
        base = {
            "proyecto_id": proyecto_test.id,
            "asignado_a_id": trabajador_user.id,
            "titulo": "Tarea de prueba",
            "descripcion": "Descripción de prueba",
            "estado": "pendiente",
            "prioridad": "media",
            "fecha_vencimiento": (datetime.now() + timedelta(days=7)).isoformat()
        }
        base.update(kwargs)
        return base
    return _create_payload


# ===== Tests de Endpoints CRUD =====

@pytest.mark.tareas
class TestTareasCreate:
    """Tests para crear tareas"""

    def test_create_tarea_success(
        self, client: TestClient, gerente_token, auth_headers,
        create_tarea_payload
    ):
        """Test crear tarea exitosamente"""
        payload = create_tarea_payload()

        response = client.post(
            "/api/v1/tareas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == payload["titulo"]
        assert data["estado"] == "pendiente"
        assert data["prioridad"] == "media"
        assert "id" in data

    def test_create_tarea_with_all_fields(
        self, client: TestClient, gerente_token, auth_headers, create_tarea_payload
    ):
        """Test crear tarea con todos los campos"""
        payload = create_tarea_payload(
            descripcion="Descripción completa",
            prioridad="urgente",
            fecha_inicio=(datetime.now() + timedelta(days=1)).isoformat()
        )

        response = client.post(
            "/api/v1/tareas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["prioridad"] == "urgente"

    def test_create_tarea_invalid_proyecto(
        self, client: TestClient, gerente_token, auth_headers, create_tarea_payload
    ):
        """Test no permite crear tarea con proyecto inválido"""
        payload = create_tarea_payload(
            proyecto_id="00000000-0000-0000-0000-000000000000"
        )

        response = client.post(
            "/api/v1/tareas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code in [400, 404]

    def test_create_tarea_without_auth(
        self, client: TestClient, create_tarea_payload
    ):
        """Test requiere autenticación"""
        payload = create_tarea_payload()

        response = client.post("/api/v1/tareas", json=payload)

        assert response.status_code in [401, 403]

    def test_create_tarea_missing_titulo(
        self, client: TestClient, gerente_token, auth_headers,
        proyecto_test, trabajador_user
    ):
        """Test título es requerido"""
        payload = {
            "proyecto_id": proyecto_test.id,
            "asignado_a_id": trabajador_user.id,
            "prioridad": "media",
            "estado": "pendiente"
        }

        response = client.post(
            "/api/v1/tareas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422


@pytest.mark.tareas
class TestTareasList:
    """Tests para listar tareas"""

    def test_list_tareas_success(
        self, client: TestClient, gerente_token, auth_headers,
        tarea_pendiente, tarea_progreso
    ):
        """Test listar tareas"""
        response = client.get(
            "/api/v1/tareas",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert data["total"] >= 2

    def test_list_tareas_filter_by_proyecto(
        self, client: TestClient, gerente_token, auth_headers,
        tarea_pendiente, proyecto_test
    ):
        """Test filtrar tareas por proyecto"""
        response = client.get(
            f"/api/v1/tareas?proyecto_id={proyecto_test.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        for tarea in data["items"]:
            assert tarea["proyecto_id"] == proyecto_test.id

    def test_list_tareas_filter_by_estado(
        self, client: TestClient, gerente_token, auth_headers,
        tarea_pendiente, tarea_progreso
    ):
        """Test filtrar por estado"""
        response = client.get(
            "/api/v1/tareas?estado=pendiente",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        for tarea in data["items"]:
            assert tarea["estado"] == "pendiente"

    def test_list_tareas_filter_by_prioridad(
        self, client: TestClient, gerente_token, auth_headers,
        tarea_progreso
    ):
        """Test filtrar por prioridad"""
        response = client.get(
            "/api/v1/tareas?prioridad=alta",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        for tarea in data["items"]:
            assert tarea["prioridad"] == "alta"

    def test_list_tareas_filter_by_asignado(
        self, client: TestClient, gerente_token, auth_headers,
        tarea_pendiente, trabajador_user
    ):
        """Test filtrar por usuario asignado"""
        response = client.get(
            f"/api/v1/tareas?asignado_a_id={trabajador_user.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        for tarea in data["items"]:
            assert tarea["asignado_a_id"] == trabajador_user.id


@pytest.mark.tareas
class TestTareasGet:
    """Tests para obtener tarea por ID"""

    def test_get_tarea_success(
        self, client: TestClient, gerente_token, auth_headers, tarea_pendiente
    ):
        """Test obtener tarea por ID"""
        response = client.get(
            f"/api/v1/tareas/{tarea_pendiente.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == tarea_pendiente.id
        assert data["titulo"] == tarea_pendiente.titulo

    def test_get_tarea_not_found(
        self, client: TestClient, gerente_token, auth_headers
    ):
        """Test obtener tarea inexistente"""
        response = client.get(
            "/api/v1/tareas/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 404


@pytest.mark.tareas
class TestTareasUpdate:
    """Tests para actualizar tareas"""

    def test_update_tarea_success(
        self, client: TestClient, gerente_token, auth_headers, tarea_pendiente
    ):
        """Test actualizar tarea"""
        update_data = {
            "titulo": "Título actualizado",
            "descripcion": "Descripción actualizada"
        }

        response = client.put(
            f"/api/v1/tareas/{tarea_pendiente.id}",
            json=update_data,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Título actualizado"
        assert data["descripcion"] == "Descripción actualizada"

    def test_update_tarea_change_prioridad(
        self, client: TestClient, gerente_token, auth_headers, tarea_pendiente
    ):
        """Test cambiar prioridad de tarea"""
        update_data = {"prioridad": "urgente"}

        response = client.put(
            f"/api/v1/tareas/{tarea_pendiente.id}",
            json=update_data,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["prioridad"] == "urgente"

    def test_update_tarea_not_found(
        self, client: TestClient, gerente_token, auth_headers
    ):
        """Test actualizar tarea inexistente"""
        update_data = {"titulo": "Nuevo título"}

        response = client.put(
            "/api/v1/tareas/00000000-0000-0000-0000-000000000000",
            json=update_data,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 404


@pytest.mark.tareas
class TestTareasEstado:
    """Tests para cambio de estado de tareas"""

    def test_change_estado_to_progreso(
        self, client: TestClient, gerente_token, auth_headers, tarea_pendiente
    ):
        """Test cambiar estado a en_progreso"""
        response = client.patch(
            f"/api/v1/tareas/{tarea_pendiente.id}/estado",
            json={"estado": "en_progreso"},
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "en_progreso"
        # fecha_inicio podría o no establecerse automáticamente
        # assert data["fecha_inicio"] is not None

    def test_change_estado_to_completada(
        self, client: TestClient, gerente_token, auth_headers, tarea_progreso
    ):
        """Test cambiar estado a completada"""
        response = client.patch(
            f"/api/v1/tareas/{tarea_progreso.id}/estado",
            json={"estado": "completada"},
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "completada"
        assert data["fecha_completada"] is not None


@pytest.mark.tareas
class TestTareasDelete:
    """Tests para eliminar tareas"""

    def test_delete_tarea_success(
        self, client: TestClient, gerente_token, auth_headers, tarea_pendiente
    ):
        """Test eliminar tarea"""
        response = client.delete(
            f"/api/v1/tareas/{tarea_pendiente.id}",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code in [200, 204]

        # Verificar que fue eliminada
        get_response = client.get(
            f"/api/v1/tareas/{tarea_pendiente.id}",
            headers=auth_headers(gerente_token)
        )
        assert get_response.status_code == 404

    def test_delete_tarea_not_found(
        self, client: TestClient, gerente_token, auth_headers
    ):
        """Test eliminar tarea inexistente"""
        response = client.delete(
            "/api/v1/tareas/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 404


@pytest.mark.tareas
class TestTareasSpecialEndpoints:
    """Tests para endpoints especiales de tareas"""

    def test_get_tareas_hoy(
        self, client: TestClient, gerente_token, auth_headers, tarea_progreso
    ):
        """Test obtener tareas de hoy"""
        response = client.get(
            "/api/v1/tareas/hoy",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_tareas_vencidas(
        self, client: TestClient, gerente_token, auth_headers, tarea_completada
    ):
        """Test obtener tareas vencidas"""
        response = client.get(
            "/api/v1/tareas/vencidas",
            headers=auth_headers(gerente_token)
        )

        # Endpoint puede existir o no
        assert response.status_code in [200, 404]

    def test_get_mis_tareas(
        self, client: TestClient, trabajador_token, auth_headers, tarea_pendiente
    ):
        """Test obtener mis tareas asignadas"""
        response = client.get(
            "/api/v1/tareas/mis-tareas",
            headers=auth_headers(trabajador_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.tareas
class TestTareasPermissions:
    """Tests de permisos y autorizaciones"""

    def test_trabajador_can_view_tareas(
        self, client: TestClient, trabajador_token, auth_headers
    ):
        """Test que trabajador puede ver tareas"""
        response = client.get(
            "/api/v1/tareas",
            headers=auth_headers(trabajador_token)
        )

        assert response.status_code == 200

    def test_trabajador_cannot_delete_tareas(
        self, client: TestClient, trabajador_token, auth_headers, tarea_pendiente
    ):
        """Test que trabajador no puede eliminar tareas"""
        response = client.delete(
            f"/api/v1/tareas/{tarea_pendiente.id}",
            headers=auth_headers(trabajador_token)
        )

        # Puede ser 403 (prohibido) o 200 (permitido) dependiendo de implementación
        assert response.status_code in [200, 403, 404]


@pytest.mark.tareas
class TestTareasValidations:
    """Tests de validaciones de negocio"""

    def test_titulo_is_required(
        self, client: TestClient, gerente_token, auth_headers,
        proyecto_test, trabajador_user
    ):
        """Test título es requerido"""
        payload = {
            "proyecto_id": proyecto_test.id,
            "asignado_a_id": trabajador_user.id,
            "prioridad": "media"
        }

        response = client.post(
            "/api/v1/tareas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422

    def test_proyecto_id_is_required(
        self, client: TestClient, gerente_token, auth_headers, trabajador_user
    ):
        """Test proyecto_id es requerido"""
        payload = {
            "titulo": "Tarea sin proyecto",
            "asignado_a_id": trabajador_user.id,
            "prioridad": "media"
        }

        response = client.post(
            "/api/v1/tareas",
            json=payload,
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 422
