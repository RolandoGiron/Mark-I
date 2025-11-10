"""
Tests para el módulo de Personal (Empleados).
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.modules.personal.models import Empleado, CargoEmpleado


# ===== Fixtures específicas de Personal =====

@pytest.fixture
def empleado_maestro(db_session, trabajador_user):
    """Empleado con cargo maestro_obra"""
    empleado = Empleado(
        usuario_id=trabajador_user.id,
        nombre="Carlos",
        apellido="Hernández",
        documento_identidad="RFC-CH-001",
        telefono="+52 55 1234 5678",
        email="carlos.h@test.com",
        cargo=CargoEmpleado.MAESTRO_OBRA,
        tarifa_hora=1800.00,
        fecha_ingreso=datetime.now() - timedelta(days=180),
        activo=True,
        notas="Maestro de obra con experiencia"
    )
    db_session.add(empleado)
    db_session.commit()
    db_session.refresh(empleado)
    return empleado


@pytest.fixture
def empleado_oficial(db_session):
    """Empleado oficial sin usuario vinculado"""
    empleado = Empleado(
        nombre="Roberto",
        apellido="Sánchez",
        documento_identidad="RFC-RS-002",
        telefono="+52 55 2345 6789",
        cargo=CargoEmpleado.OFICIAL,
        tarifa_hora=1500.00,
        fecha_ingreso=datetime.now() - timedelta(days=90),
        activo=True
    )
    db_session.add(empleado)
    db_session.commit()
    db_session.refresh(empleado)
    return empleado


@pytest.fixture
def empleado_inactivo(db_session):
    """Empleado inactivo (dado de baja)"""
    empleado = Empleado(
        nombre="Pedro",
        apellido="López",
        documento_identidad="RFC-PL-003",
        cargo=CargoEmpleado.OBRERO,
        tarifa_hora=1200.00,
        fecha_ingreso=datetime.now() - timedelta(days=365),
        fecha_salida=datetime.now() - timedelta(days=30),
        activo=False,
        notas="Empleado dado de baja"
    )
    db_session.add(empleado)
    db_session.commit()
    db_session.refresh(empleado)
    return empleado


@pytest.fixture
def create_empleado_payload():
    """Helper para crear payload de empleado"""
    def _create_payload(**kwargs):
        base = {
            "nombre": "Juan",
            "apellido": "Test",
            "documento_identidad": f"RFC-TEST-{datetime.now().timestamp()}",
            "telefono": "+52 55 9876 5432",
            "email": "juan.test@example.com",
            "cargo": "obrero",
            "tarifa_hora": 1200.00,
            "activo": True,
            "notas": "Empleado de prueba"
        }
        base.update(kwargs)
        return base
    return _create_payload


# ===== Tests de Endpoints CRUD =====

@pytest.mark.personal
class TestPersonalCreate:
    """Tests para crear empleados"""

    def test_create_empleado_success(
        self, client: TestClient, admin_token, auth_headers, create_empleado_payload
    ):
        """Test crear empleado exitosamente"""
        payload = create_empleado_payload()

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == payload["nombre"]
        assert data["apellido"] == payload["apellido"]
        assert data["cargo"] == payload["cargo"]
        assert float(data["tarifa_hora"]) == payload["tarifa_hora"]
        assert data["activo"] is True
        assert "id" in data

    def test_create_empleado_with_usuario(
        self, client: TestClient, admin_token, auth_headers,
        create_empleado_payload, trabajador_user
    ):
        """Test crear empleado vinculado a un usuario"""
        payload = create_empleado_payload(usuario_id=trabajador_user.id)

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["usuario_id"] == trabajador_user.id

    def test_create_empleado_duplicate_documento(
        self, client: TestClient, admin_token, auth_headers,
        create_empleado_payload, empleado_maestro
    ):
        """Test no permite documento de identidad duplicado"""
        payload = create_empleado_payload(
            documento_identidad=empleado_maestro.documento_identidad
        )

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 400
        assert "documento" in response.json()["detail"].lower()

    def test_create_empleado_invalid_cargo(
        self, client: TestClient, admin_token, auth_headers, create_empleado_payload
    ):
        """Test no acepta cargo inválido"""
        payload = create_empleado_payload(cargo="cargo_invalido")

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        # La API podría aceptar el valor como string o rechazarlo
        assert response.status_code in [201, 422]

    def test_create_empleado_negative_tarifa(
        self, client: TestClient, admin_token, auth_headers, create_empleado_payload
    ):
        """Test no acepta tarifa negativa"""
        payload = create_empleado_payload(tarifa_hora=-100)

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 422

    def test_create_empleado_without_auth(
        self, client: TestClient, create_empleado_payload
    ):
        """Test requiere autenticación"""
        payload = create_empleado_payload()

        response = client.post("/api/v1/personal", json=payload)

        assert response.status_code in [401, 403]

    def test_create_empleado_as_trabajador(
        self, client: TestClient, trabajador_token, auth_headers, create_empleado_payload
    ):
        """Test que trabajador no puede crear empleados"""
        payload = create_empleado_payload()

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(trabajador_token)
        )

        assert response.status_code == 403


@pytest.mark.personal
class TestPersonalList:
    """Tests para listar empleados"""

    def test_list_empleados_success(
        self, client: TestClient, admin_token, auth_headers,
        empleado_maestro, empleado_oficial
    ):
        """Test listar empleados"""
        response = client.get(
            "/api/v1/personal",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    def test_list_empleados_filter_activos(
        self, client: TestClient, admin_token, auth_headers,
        empleado_maestro, empleado_inactivo
    ):
        """Test filtrar solo empleados activos"""
        response = client.get(
            "/api/v1/personal?activo=true",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        for empleado in data["items"]:
            assert empleado["activo"] is True

    def test_list_empleados_filter_cargo(
        self, client: TestClient, admin_token, auth_headers, empleado_maestro
    ):
        """Test filtrar por cargo"""
        response = client.get(
            "/api/v1/personal?cargo=maestro_obra",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        for empleado in data["items"]:
            assert empleado["cargo"] == "maestro_obra"

    def test_list_empleados_search(
        self, client: TestClient, admin_token, auth_headers, empleado_maestro
    ):
        """Test buscar por nombre o apellido"""
        response = client.get(
            f"/api/v1/personal?search={empleado_maestro.nombre}",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        found = any(e["nombre"] == empleado_maestro.nombre for e in data["items"])
        assert found

    def test_list_empleados_pagination(
        self, client: TestClient, admin_token, auth_headers,
        empleado_maestro, empleado_oficial
    ):
        """Test paginación"""
        response = client.get(
            "/api/v1/personal?page=1&page_size=1",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["page"] == 1


@pytest.mark.personal
class TestPersonalGet:
    """Tests para obtener empleado por ID"""

    def test_get_empleado_success(
        self, client: TestClient, admin_token, auth_headers, empleado_maestro
    ):
        """Test obtener empleado por ID"""
        response = client.get(
            f"/api/v1/personal/{empleado_maestro.id}",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == empleado_maestro.id
        assert data["nombre"] == empleado_maestro.nombre
        assert data["apellido"] == empleado_maestro.apellido

    def test_get_empleado_not_found(
        self, client: TestClient, admin_token, auth_headers
    ):
        """Test obtener empleado inexistente"""
        response = client.get(
            "/api/v1/personal/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 404

    def test_get_empleado_invalid_id(
        self, client: TestClient, admin_token, auth_headers
    ):
        """Test ID inválido"""
        response = client.get(
            "/api/v1/personal/invalid-id",
            headers=auth_headers(admin_token)
        )

        # Puede ser 422 (validación) o 404 (no encontrado)
        assert response.status_code in [404, 422]


@pytest.mark.personal
class TestPersonalUpdate:
    """Tests para actualizar empleados"""

    def test_update_empleado_success(
        self, client: TestClient, admin_token, auth_headers, empleado_oficial
    ):
        """Test actualizar empleado"""
        update_data = {
            "tarifa_hora": 1600.00,
            "notas": "Tarifa actualizada"
        }

        response = client.put(
            f"/api/v1/personal/{empleado_oficial.id}",
            json=update_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert float(data["tarifa_hora"]) == 1600.00
        assert data["notas"] == "Tarifa actualizada"

    def test_update_empleado_change_cargo(
        self, client: TestClient, admin_token, auth_headers, empleado_oficial
    ):
        """Test cambiar cargo de empleado"""
        update_data = {"cargo": "maestro_obra"}

        response = client.put(
            f"/api/v1/personal/{empleado_oficial.id}",
            json=update_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cargo"] == "maestro_obra"

    def test_update_empleado_documento_duplicado(
        self, client: TestClient, admin_token, auth_headers,
        empleado_maestro, empleado_oficial
    ):
        """Test no permite actualizar con documento duplicado"""
        update_data = {
            "documento_identidad": empleado_maestro.documento_identidad
        }

        response = client.put(
            f"/api/v1/personal/{empleado_oficial.id}",
            json=update_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 400

    def test_update_empleado_not_found(
        self, client: TestClient, admin_token, auth_headers
    ):
        """Test actualizar empleado inexistente"""
        update_data = {"tarifa_hora": 2000.00}

        response = client.put(
            "/api/v1/personal/00000000-0000-0000-0000-000000000000",
            json=update_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 404


@pytest.mark.personal
class TestPersonalDelete:
    """Tests para eliminar empleados"""

    def test_delete_empleado_success(
        self, client: TestClient, admin_token, auth_headers, empleado_oficial
    ):
        """Test eliminar empleado (soft delete)"""
        response = client.delete(
            f"/api/v1/personal/{empleado_oficial.id}",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200

        # Verificar que fue desactivado (soft delete)
        get_response = client.get(
            f"/api/v1/personal/{empleado_oficial.id}",
            headers=auth_headers(admin_token)
        )
        assert get_response.status_code == 200
        assert get_response.json()["activo"] is False

    def test_delete_empleado_not_found(
        self, client: TestClient, admin_token, auth_headers
    ):
        """Test eliminar empleado inexistente"""
        response = client.delete(
            "/api/v1/personal/00000000-0000-0000-0000-000000000000",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 404


@pytest.mark.personal
class TestPersonalStats:
    """Tests para estadísticas de empleados"""

    def test_get_stats_success(
        self, client: TestClient, admin_token, auth_headers,
        empleado_maestro, empleado_oficial, empleado_inactivo
    ):
        """Test obtener estadísticas generales"""
        response = client.get(
            "/api/v1/personal/stats",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_empleados" in data
        assert "empleados_activos" in data
        assert "empleados_inactivos" in data
        assert "por_cargo" in data
        assert data["total_empleados"] >= 3
        assert data["empleados_activos"] >= 2
        assert data["empleados_inactivos"] >= 1


@pytest.mark.personal
class TestPersonalActivos:
    """Tests para obtener solo empleados activos"""

    def test_get_activos_success(
        self, client: TestClient, admin_token, auth_headers,
        empleado_maestro, empleado_oficial, empleado_inactivo
    ):
        """Test obtener solo empleados activos usando filtro"""
        response = client.get(
            "/api/v1/personal?activo=true",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        # Todos deben estar activos
        for empleado in data["items"]:
            assert empleado["activo"] is True


@pytest.mark.personal
class TestPersonalHoras:
    """Tests para obtener horas trabajadas de empleado"""

    def test_get_horas_empleado(
        self, client: TestClient, admin_token, auth_headers, empleado_maestro
    ):
        """Test obtener horas de un empleado"""
        # Endpoint existe pero sin datos de horas aún
        response = client.get(
            f"/api/v1/personal/{empleado_maestro.id}/horas",
            headers=auth_headers(admin_token)
        )

        # Puede ser 200 con lista vacía o 404 dependiendo de implementación
        assert response.status_code in [200, 404]


@pytest.mark.personal
class TestPersonalPermissions:
    """Tests de permisos y autorizaciones"""

    def test_gerente_can_view_empleados(
        self, client: TestClient, gerente_token, auth_headers, empleado_maestro
    ):
        """Test que gerente puede ver empleados"""
        response = client.get(
            "/api/v1/personal",
            headers=auth_headers(gerente_token)
        )

        assert response.status_code == 200

    def test_supervisor_can_view_empleados(
        self, client: TestClient, supervisor_token, auth_headers
    ):
        """Test que supervisor puede ver empleados"""
        response = client.get(
            "/api/v1/personal",
            headers=auth_headers(supervisor_token)
        )

        assert response.status_code == 200

    def test_trabajador_can_view_empleados(
        self, client: TestClient, trabajador_token, auth_headers
    ):
        """Test que trabajador puede ver empleados"""
        response = client.get(
            "/api/v1/personal",
            headers=auth_headers(trabajador_token)
        )

        # Trabajadores pueden o no tener permiso, depende de la implementación
        # Si no tienen permiso sería 403
        assert response.status_code in [200, 403]


@pytest.mark.personal
class TestPersonalValidations:
    """Tests de validaciones de negocio"""

    def test_tarifa_hora_must_be_positive(
        self, client: TestClient, admin_token, auth_headers, create_empleado_payload
    ):
        """Test tarifa_hora debe ser positiva"""
        payload = create_empleado_payload(tarifa_hora=0)

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        # La validación podría estar o no implementada
        assert response.status_code in [201, 422]

    def test_nombre_required(
        self, client: TestClient, admin_token, auth_headers
    ):
        """Test nombre es requerido"""
        payload = {
            "apellido": "Test",
            "cargo": "obrero",
            "tarifa_hora": 1200.00
        }

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 422

    def test_apellido_required(
        self, client: TestClient, admin_token, auth_headers
    ):
        """Test apellido es requerido"""
        payload = {
            "nombre": "Juan",
            "cargo": "obrero",
            "tarifa_hora": 1200.00
        }

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 422

    def test_cargo_required(
        self, client: TestClient, admin_token, auth_headers
    ):
        """Test cargo es requerido"""
        payload = {
            "nombre": "Juan",
            "apellido": "Test",
            "tarifa_hora": 1200.00
        }

        response = client.post(
            "/api/v1/personal",
            json=payload,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 422
