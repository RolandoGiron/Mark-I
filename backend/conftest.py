"""
Configuración de fixtures globales para pytest.
Este archivo contiene todas las fixtures compartidas entre los tests.
"""

import os
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.config import Settings, get_settings
from app.modules.auth.models import Usuario, RolUsuario
from app.modules.auth.utils import hash_password


# ===== Configuración de Testing =====

class TestSettings(Settings):
    """Configuración específica para tests"""
    ENVIRONMENT: str = "testing"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "test-secret-key-super-secure-for-testing-only"
    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = "./test_uploads"

    model_config = {
        "env_file": None,  # No cargar .env en tests
        "extra": "ignore"
    }


@pytest.fixture(scope="session")
def test_settings():
    """Settings para testing"""
    return TestSettings()


# ===== Database Fixtures =====

@pytest.fixture(scope="function")
def db_engine(test_settings):
    """
    Crea un engine de base de datos para tests.
    Scope: function - se crea una nueva DB para cada test.
    """
    engine = create_engine(
        test_settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    yield engine

    # Limpiar después del test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    # Eliminar archivo de BD de test
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """
    Crea una sesión de base de datos para tests.
    Cada test obtiene una sesión limpia.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session, test_settings):
    """
    Cliente de prueba de FastAPI con DB de test.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_settings():
        return test_settings

    # Override dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = override_get_settings

    with TestClient(app) as test_client:
        yield test_client

    # Limpiar overrides
    app.dependency_overrides.clear()


# ===== User Fixtures =====

@pytest.fixture
def password_plain():
    """Contraseña en texto plano para tests"""
    return "Test123456"


@pytest.fixture
def admin_user(db_session, password_plain) -> Usuario:
    """Usuario con rol ADMIN"""
    user = Usuario(
        username="admin_test",
        email="admin@test.com",
        nombre_completo="Admin Test",
        hashed_password=hash_password(password_plain),
        rol=RolUsuario.ADMIN,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def gerente_user(db_session, password_plain) -> Usuario:
    """Usuario con rol GERENTE"""
    user = Usuario(
        username="gerente_test",
        email="gerente@test.com",
        nombre_completo="Gerente Test",
        hashed_password=hash_password(password_plain),
        rol=RolUsuario.GERENTE,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def supervisor_user(db_session, password_plain) -> Usuario:
    """Usuario con rol SUPERVISOR"""
    user = Usuario(
        username="supervisor_test",
        email="supervisor@test.com",
        nombre_completo="Supervisor Test",
        hashed_password=hash_password(password_plain),
        rol=RolUsuario.SUPERVISOR,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def trabajador_user(db_session, password_plain) -> Usuario:
    """Usuario con rol TRABAJADOR"""
    user = Usuario(
        username="trabajador_test",
        email="trabajador@test.com",
        nombre_completo="Trabajador Test",
        hashed_password=hash_password(password_plain),
        rol=RolUsuario.TRABAJADOR,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session, password_plain) -> Usuario:
    """Usuario inactivo"""
    user = Usuario(
        username="inactive_test",
        email="inactive@test.com",
        nombre_completo="Inactive Test",
        hashed_password=hash_password(password_plain),
        rol=RolUsuario.TRABAJADOR,
        activo=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ===== Token Fixtures =====

@pytest.fixture
def admin_token(client, admin_user, password_plain) -> str:
    """Token JWT de admin"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": admin_user.username, "password": password_plain}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def gerente_token(client, gerente_user, password_plain) -> str:
    """Token JWT de gerente"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": gerente_user.username, "password": password_plain}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def supervisor_token(client, supervisor_user, password_plain) -> str:
    """Token JWT de supervisor"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": supervisor_user.username, "password": password_plain}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def trabajador_token(client, trabajador_user, password_plain) -> str:
    """Token JWT de trabajador"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": trabajador_user.username, "password": password_plain}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# ===== Helper Fixtures =====

@pytest.fixture
def auth_headers():
    """Helper para crear headers de autenticación"""
    def _auth_headers(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers


@pytest.fixture
def create_user_payload():
    """Helper para crear payload de usuario"""
    def _create_payload(username: str, email: str, rol: str = "trabajador") -> dict:
        return {
            "username": username,
            "email": email,
            "nombre_completo": f"Test User {username}",
            "password": "Test123456",
            "telefono": "+52 1 55 1234 5678",
            "rol": rol
        }
    return _create_payload


# ===== Cleanup Fixtures =====

@pytest.fixture(autouse=True)
def cleanup_test_uploads(test_settings):
    """Limpia el directorio de uploads de test después de cada test"""
    yield

    # Cleanup
    upload_dir = test_settings.UPLOAD_DIR
    if os.path.exists(upload_dir):
        import shutil
        shutil.rmtree(upload_dir)
