"""
Tests para el módulo de autenticación.
"""

import pytest
from fastapi.testclient import TestClient
from app.modules.auth.models import Usuario, RolUsuario


@pytest.mark.auth
class TestAuthRegister:
    """Tests para el endpoint de registro"""

    def test_register_success(self, client: TestClient, create_user_payload):
        """Test de registro exitoso"""
        payload = create_user_payload("nuevouser", "nuevo@test.com")

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "nuevouser"
        assert data["email"] == "nuevo@test.com"
        assert data["activo"] is True
        assert "password" not in data
        assert "id" in data

    def test_register_duplicate_username(self, client: TestClient, create_user_payload, admin_user):
        """Test de registro con username duplicado"""
        payload = create_user_payload(admin_user.username, "otro@test.com")

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_register_duplicate_email(self, client: TestClient, create_user_payload, admin_user):
        """Test de registro con email duplicado"""
        payload = create_user_payload("otrousername", admin_user.email)

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test de registro con email inválido"""
        payload = {
            "username": "testuser",
            "email": "invalid-email",
            "nombre_completo": "Test User",
            "password": "Test123456",
            "rol": "trabajador"
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Test de registro con contraseña corta"""
        payload = {
            "username": "testuser",
            "email": "test@test.com",
            "nombre_completo": "Test User",
            "password": "123",  # Menos de 6 caracteres
            "rol": "trabajador"
        }

        response = client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    def test_register_with_different_roles(self, client: TestClient, create_user_payload):
        """Test de registro con diferentes roles"""
        roles = ["admin", "gerente", "supervisor", "trabajador"]

        for rol in roles:
            username = f"user_{rol}"
            payload = create_user_payload(username, f"{username}@test.com", rol)

            response = client.post("/api/v1/auth/register", json=payload)

            assert response.status_code == 201
            assert response.json()["rol"] == rol


@pytest.mark.auth
class TestAuthLogin:
    """Tests para el endpoint de login"""

    def test_login_success_with_username(self, client: TestClient, admin_user, password_plain):
        """Test de login exitoso con username"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": password_plain}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == admin_user.username

    def test_login_success_with_email(self, client: TestClient, admin_user, password_plain):
        """Test de login exitoso con email"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.email, "password": password_plain}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == admin_user.email

    def test_login_wrong_password(self, client: TestClient, admin_user):
        """Test de login con contraseña incorrecta"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "wrongpassword"}
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Test de login con usuario inexistente"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "noexiste", "password": "password123"}
        )

        assert response.status_code == 401

    def test_login_inactive_user(self, client: TestClient, inactive_user, password_plain):
        """Test de login con usuario inactivo"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": inactive_user.username, "password": password_plain}
        )

        # Puede ser 401 (Unauthorized) o 403 (Forbidden) para usuarios inactivos
        assert response.status_code in [401, 403]


@pytest.mark.auth
class TestAuthMe:
    """Tests para endpoints de usuario actual"""

    def test_get_me_success(self, client: TestClient, admin_token, admin_user, auth_headers):
        """Test de obtener usuario actual"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == admin_user.username
        assert data["email"] == admin_user.email
        assert "password" not in data

    def test_get_me_without_token(self, client: TestClient):
        """Test de obtener usuario sin token"""
        response = client.get("/api/v1/auth/me")

        # Puede ser 401 (Unauthorized) o 403 (Forbidden) dependiendo de la implementación
        assert response.status_code in [401, 403]

    def test_get_me_invalid_token(self, client: TestClient, auth_headers):
        """Test de obtener usuario con token inválido"""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers("invalid-token")
        )

        assert response.status_code == 401

    def test_update_me_success(self, client: TestClient, admin_token, auth_headers):
        """Test de actualizar perfil propio"""
        update_data = {
            "nombre_completo": "Nombre Actualizado",
            "telefono": "+52 1 55 9999 9999"
        }

        response = client.put(
            "/api/v1/auth/me",
            json=update_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre_completo"] == "Nombre Actualizado"
        assert data["telefono"] == "+52 1 55 9999 9999"

    def test_update_me_cannot_change_role_non_admin(
        self, client: TestClient, trabajador_token, auth_headers
    ):
        """Test que usuario no-admin no puede cambiar su rol"""
        update_data = {"rol": "admin"}

        response = client.put(
            "/api/v1/auth/me",
            json=update_data,
            headers=auth_headers(trabajador_token)
        )

        assert response.status_code == 200
        # El rol no debería cambiar
        assert response.json()["rol"] == "trabajador"

    def test_change_password_success(self, client: TestClient, admin_user, admin_token, password_plain, auth_headers):
        """Test de cambio de contraseña exitoso"""
        change_data = {
            "current_password": password_plain,
            "new_password": "NewPassword123"
        }

        response = client.post(
            "/api/v1/auth/me/change-password",
            json=change_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200

        # Verificar que puede hacer login con la nueva contraseña
        login_response = client.post(
            "/api/v1/auth/login",
            json={"username": admin_user.username, "password": "NewPassword123"}
        )
        assert login_response.status_code == 200

    def test_change_password_wrong_current(self, client: TestClient, admin_token, auth_headers):
        """Test de cambio de contraseña con contraseña actual incorrecta"""
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123"
        }

        response = client.post(
            "/api/v1/auth/me/change-password",
            json=change_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 400


@pytest.mark.auth
@pytest.mark.admin
class TestAuthAdmin:
    """Tests para endpoints de administración de usuarios"""

    def test_list_usuarios_as_admin(self, client: TestClient, admin_token, auth_headers):
        """Test listar usuarios como admin"""
        response = client.get(
            "/api/v1/auth/usuarios",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "items" in data
        assert "page" in data
        assert len(data["items"]) > 0

    def test_list_usuarios_as_non_admin(self, client: TestClient, trabajador_token, auth_headers):
        """Test que no-admin no puede listar usuarios"""
        response = client.get(
            "/api/v1/auth/usuarios",
            headers=auth_headers(trabajador_token)
        )

        assert response.status_code == 403

    def test_list_usuarios_with_filters(
        self, client: TestClient, admin_token, gerente_user, auth_headers
    ):
        """Test listar usuarios con filtros"""
        response = client.get(
            "/api/v1/auth/usuarios?rol=gerente&activo=true",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        # Debe haber al menos el gerente_user
        assert data["total"] >= 1
        for user in data["items"]:
            assert user["rol"] == "gerente"

    def test_get_usuario_by_id_as_admin(
        self, client: TestClient, admin_token, trabajador_user, auth_headers
    ):
        """Test obtener usuario por ID como admin"""
        response = client.get(
            f"/api/v1/auth/usuarios/{trabajador_user.id}",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == trabajador_user.id
        assert data["username"] == trabajador_user.username

    def test_update_usuario_as_admin(
        self, client: TestClient, admin_token, trabajador_user, auth_headers
    ):
        """Test actualizar usuario como admin"""
        update_data = {
            "nombre_completo": "Nombre Actualizado por Admin",
            "rol": "supervisor"
        }

        response = client.put(
            f"/api/v1/auth/usuarios/{trabajador_user.id}",
            json=update_data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre_completo"] == "Nombre Actualizado por Admin"
        assert data["rol"] == "supervisor"

    def test_delete_usuario_as_admin(
        self, client: TestClient, admin_token, trabajador_user, auth_headers
    ):
        """Test eliminar usuario como admin"""
        response = client.delete(
            f"/api/v1/auth/usuarios/{trabajador_user.id}",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200

        # Verificar que el usuario ya no existe
        get_response = client.get(
            f"/api/v1/auth/usuarios/{trabajador_user.id}",
            headers=auth_headers(admin_token)
        )
        assert get_response.status_code == 404

    def test_delete_self_as_admin(self, client: TestClient, admin_token, admin_user, auth_headers):
        """Test que admin no puede eliminarse a sí mismo"""
        response = client.delete(
            f"/api/v1/auth/usuarios/{admin_user.id}",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 400
        assert "propio" in response.json()["detail"].lower()
