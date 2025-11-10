# Backend Testing Setup Guide

## Overview

This guide provides step-by-step instructions to set up comprehensive testing for the Mark-I backend API.

## Current Status

- Pytest framework installed: YES
- Testing libraries available: YES (pytest, pytest-asyncio, pytest-cov, httpx)
- Existing tests: NONE (empty tests/ directory)
- Test configuration: NOT YET CREATED

---

## Step 1: Create Test Configuration Files

### 1.1 Create `pytest.ini`

Location: `/home/rolando/Desarrollo/Mark-I/backend/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
minversion = 7.0

markers =
    unit: Unit tests (services and utilities)
    integration: Integration tests (full request cycle)
    e2e: End-to-end tests (complete workflows)
    slow: Tests that take more than 1 second
    auth: Authentication related tests
    projects: Projects module tests
    expenses: Expenses module tests

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### 1.2 Create `.coveragerc`

Location: `/home/rolando/Desarrollo/Mark-I/backend/.coveragerc`

```ini
[run]
source = app
omit =
    */migrations/*
    */tests/*
    */__init__.py
    */main.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
    @abstractproperty
precision = 2
skip_covered = False
show_missing = True

[html]
directory = htmlcov
```

---

## Step 2: Create Test Fixtures

### 2.1 Create `tests/conftest.py`

Main fixture file with shared test setup:

```python
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.modules.auth.models import Usuario, RolUsuario
from app.modules.proyectos.models import Proyecto, EstadoProyecto
from app.modules.costos.models import Costo, CategoriaGasto, MetodoCaptura
from app.modules.auth.utils import hash_password, create_access_token


# Test Database Setup
@pytest.fixture(scope="session")
def test_db_url():
    """Use in-memory SQLite for tests"""
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine(test_db_url):
    """Create test database engine"""
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def db_session(engine):
    """Provide a fresh test database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    # Override get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Provide FastAPI TestClient with test database"""
    return TestClient(app)


# User Fixtures
@pytest.fixture
def admin_user(db_session) -> Usuario:
    """Create and return admin test user"""
    user = Usuario(
        id="admin-uuid",
        username="admin",
        email="admin@test.com",
        hashed_password=hash_password("admin123"),
        nombre_completo="Admin User",
        rol=RolUsuario.ADMIN,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def gerente_user(db_session) -> Usuario:
    """Create and return gerente test user"""
    user = Usuario(
        id="gerente-uuid",
        username="gerente",
        email="gerente@test.com",
        hashed_password=hash_password("gerente123"),
        nombre_completo="Gerente User",
        rol=RolUsuario.GERENTE,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def supervisor_user(db_session) -> Usuario:
    """Create and return supervisor test user"""
    user = Usuario(
        id="supervisor-uuid",
        username="supervisor",
        email="supervisor@test.com",
        hashed_password=hash_password("supervisor123"),
        nombre_completo="Supervisor User",
        rol=RolUsuario.SUPERVISOR,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def trabajador_user(db_session) -> Usuario:
    """Create and return trabajador test user"""
    user = Usuario(
        id="trabajador-uuid",
        username="trabajador",
        email="trabajador@test.com",
        hashed_password=hash_password("trabajador123"),
        nombre_completo="Trabajador User",
        rol=RolUsuario.TRABAJADOR,
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    return user


# Token Fixtures
@pytest.fixture
def admin_token(admin_user) -> str:
    """Generate JWT token for admin user"""
    return create_access_token(
        data={
            "sub": admin_user.id,
            "username": admin_user.username,
            "rol": admin_user.rol.value
        }
    )


@pytest.fixture
def admin_headers(admin_token) -> dict:
    """Return authorization headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def gerente_token(gerente_user) -> str:
    """Generate JWT token for gerente user"""
    return create_access_token(
        data={
            "sub": gerente_user.id,
            "username": gerente_user.username,
            "rol": gerente_user.rol.value
        }
    )


@pytest.fixture
def gerente_headers(gerente_token) -> dict:
    """Return authorization headers with gerente token"""
    return {"Authorization": f"Bearer {gerente_token}"}


# Project Fixtures
@pytest.fixture
def sample_project(db_session) -> Proyecto:
    """Create sample project for testing"""
    project = Proyecto(
        id="project-1-uuid",
        codigo="TEST-001",
        nombre="Test Project",
        cliente="Test Client",
        descripcion="A test project for unit testing",
        fecha_inicio=datetime.utcnow(),
        fecha_fin_estimada=datetime.utcnow() + timedelta(days=30),
        presupuesto_total=50000.00,
        horas_presupuestadas=100.00,
        estado=EstadoProyecto.EN_PROGRESO
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def sample_projects(db_session, sample_project) -> list:
    """Create multiple sample projects for testing"""
    projects = [
        sample_project,
        Proyecto(
            id="project-2-uuid",
            codigo="TEST-002",
            nombre="Completed Project",
            cliente="Another Client",
            presupuesto_total=30000.00,
            estado=EstadoProyecto.COMPLETADO
        ),
        Proyecto(
            id="project-3-uuid",
            codigo="TEST-003",
            nombre="Paused Project",
            cliente="Yet Another Client",
            presupuesto_total=20000.00,
            estado=EstadoProyecto.PAUSADO
        )
    ]
    db_session.add_all(projects[1:])
    db_session.commit()
    return projects


# Expense Fixtures
@pytest.fixture
def sample_expense(db_session, sample_project) -> Costo:
    """Create sample expense for testing"""
    expense = Costo(
        id="expense-1-uuid",
        proyecto_id=sample_project.id,
        categoria=CategoriaGasto.MATERIALES,
        monto=1500.00,
        descripcion="Concrete and sand",
        proveedor_nombre="ABC Hardware",
        fecha_gasto=datetime.utcnow(),
        metodo_captura=MetodoCaptura.MANUAL_WEB,
        validado=False
    )
    db_session.add(expense)
    db_session.commit()
    return expense


@pytest.fixture
def sample_expenses(db_session, sample_project) -> list:
    """Create multiple sample expenses for testing"""
    expenses = [
        Costo(
            id="expense-1-uuid",
            proyecto_id=sample_project.id,
            categoria=CategoriaGasto.MATERIALES,
            monto=1500.00,
            descripcion="Materials",
            fecha_gasto=datetime.utcnow(),
            validado=False
        ),
        Costo(
            id="expense-2-uuid",
            proyecto_id=sample_project.id,
            categoria=CategoriaGasto.MANO_OBRA,
            monto=2000.00,
            descripcion="Labor",
            fecha_gasto=datetime.utcnow(),
            validado=True
        ),
        Costo(
            id="expense-3-uuid",
            proyecto_id=sample_project.id,
            categoria=CategoriaGasto.TRANSPORTE,
            monto=500.00,
            descripcion="Transportation",
            fecha_gasto=datetime.utcnow(),
            validado=False
        )
    ]
    db_session.add_all(expenses)
    db_session.commit()
    return expenses
```

---

## Step 3: Create Unit Tests

### 3.1 Create `tests/unit/test_auth_services.py`

```python
import pytest
from fastapi import HTTPException, status

from app.modules.auth.services import AuthService
from app.modules.auth.schemas import UsuarioCreate, LoginRequest, ChangePasswordRequest
from app.modules.auth.models import RolUsuario


@pytest.mark.unit
@pytest.mark.auth
class TestAuthService:
    """Tests for AuthService business logic"""
    
    def test_register_success(self, db_session):
        """Test successful user registration"""
        service = AuthService(db_session)
        
        user_data = UsuarioCreate(
            username="newuser",
            email="new@test.com",
            password="password123",
            nombre_completo="New User"
        )
        
        result = service.register(user_data)
        
        assert result.username == "newuser"
        assert result.email == "new@test.com"
        assert result.nombre_completo == "New User"
    
    def test_register_duplicate_username(self, db_session, admin_user):
        """Test registration fails with duplicate username"""
        service = AuthService(db_session)
        
        user_data = UsuarioCreate(
            username="admin",  # Already exists
            email="different@test.com",
            password="password123",
            nombre_completo="Different User"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.register(user_data)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "already" in str(exc_info.value.detail).lower()
    
    def test_login_success(self, db_session, admin_user):
        """Test successful login"""
        service = AuthService(db_session)
        
        login_data = LoginRequest(username="admin", password="admin123")
        result = service.login(login_data)
        
        assert result.access_token
        assert result.user.username == "admin"
    
    def test_login_invalid_password(self, db_session, admin_user):
        """Test login fails with wrong password"""
        service = AuthService(db_session)
        
        login_data = LoginRequest(username="admin", password="wrongpassword")
        
        with pytest.raises(HTTPException) as exc_info:
            service.login(login_data)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, db_session):
        """Test login fails for non-existent user"""
        service = AuthService(db_session)
        
        login_data = LoginRequest(username="nonexistent", password="password123")
        
        with pytest.raises(HTTPException) as exc_info:
            service.login(login_data)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_usuario_by_id(self, db_session, admin_user):
        """Test retrieving user by ID"""
        service = AuthService(db_session)
        
        result = service.get_usuario_by_id(admin_user.id)
        
        assert result.id == admin_user.id
        assert result.username == "admin"
```

### 3.2 Create `tests/unit/test_proyecto_services.py`

```python
import pytest
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.modules.proyectos.services import ProyectoService
from app.modules.proyectos.schemas import ProyectoCreate, ProyectoUpdate
from app.modules.proyectos.models import EstadoProyecto


@pytest.mark.unit
@pytest.mark.projects
class TestProyectoService:
    """Tests for ProyectoService business logic"""
    
    def test_create_proyecto_success(self, db_session):
        """Test successful project creation"""
        service = ProyectoService(db_session)
        
        proyecto_data = ProyectoCreate(
            codigo="NEW-001",
            nombre="New Project",
            cliente="New Client",
            presupuesto_total=100000.00
        )
        
        result = service.create_proyecto(proyecto_data)
        
        assert result.codigo == "NEW-001"
        assert result.nombre == "New Project"
        assert result.presupuesto_total == 100000.00
    
    def test_create_proyecto_duplicate_code(self, db_session, sample_project):
        """Test project creation fails with duplicate code"""
        service = ProyectoService(db_session)
        
        proyecto_data = ProyectoCreate(
            codigo=sample_project.codigo,  # Duplicate
            nombre="Another Project",
            cliente="Another Client",
            presupuesto_total=50000.00
        )
        
        with pytest.raises(HTTPException):
            service.create_proyecto(proyecto_data)
    
    def test_get_proyecto_by_id(self, db_session, sample_project):
        """Test retrieving project by ID"""
        service = ProyectoService(db_session)
        
        result = service.get_proyecto_by_id(sample_project.id)
        
        assert result.id == sample_project.id
        assert result.codigo == sample_project.codigo
    
    def test_get_proyecto_by_codigo(self, db_session, sample_project):
        """Test retrieving project by code"""
        service = ProyectoService(db_session)
        
        result = service.get_proyecto_by_codigo(sample_project.codigo)
        
        assert result.codigo == sample_project.codigo
    
    def test_update_proyecto(self, db_session, sample_project):
        """Test updating project"""
        service = ProyectoService(db_session)
        
        update_data = ProyectoUpdate(
            nombre="Updated Name",
            estado=EstadoProyecto.COMPLETADO
        )
        
        result = service.update_proyecto(sample_project.id, update_data)
        
        assert result.nombre == "Updated Name"
        assert result.estado == EstadoProyecto.COMPLETADO
    
    def test_get_proyectos_pagination(self, db_session, sample_projects):
        """Test listing projects with pagination"""
        service = ProyectoService(db_session)
        
        proyectos, total = service.get_proyectos(skip=0, limit=2)
        
        assert len(proyectos) == 2
        assert total == 3
    
    def test_get_resumen_financiero(self, db_session, sample_project, sample_expense):
        """Test financial summary calculation"""
        service = ProyectoService(db_session)
        
        result = service.get_resumen_financiero(sample_project.id)
        
        assert result.presupuesto_total == sample_project.presupuesto_total
        assert result.total_gastado == sample_expense.monto
```

---

## Step 4: Create Integration Tests

### 4.1 Create `tests/integration/test_auth_routes.py`

```python
import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRoutes:
    """Integration tests for authentication endpoints"""
    
    def test_register_endpoint(self, client):
        """Test POST /auth/register"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "nombre_completo": "Test User"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_login_endpoint(self, client, admin_user):
        """Test POST /auth/login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "admin123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["user"]["username"] == "admin"
    
    def test_get_me_authenticated(self, client, admin_headers):
        """Test GET /auth/me with valid token"""
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "admin"
    
    def test_get_me_unauthenticated(self, client):
        """Test GET /auth/me without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_usuarios_admin_only(self, client, admin_headers, gerente_headers):
        """Test that only admin can list users"""
        # Admin should succeed
        response = client.get("/api/v1/auth/usuarios", headers=admin_headers)
        assert response.status_code == status.HTTP_200_OK
        
        # Gerente should fail
        response = client.get("/api/v1/auth/usuarios", headers=gerente_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
```

### 4.2 Create `tests/integration/test_proyectos_routes.py`

```python
import pytest
from fastapi import status


@pytest.mark.integration
@pytest.mark.projects
class TestProyectosRoutes:
    """Integration tests for project endpoints"""
    
    def test_create_project(self, client, admin_headers):
        """Test POST /proyectos"""
        response = client.post(
            "/api/v1/proyectos",
            headers=admin_headers,
            json={
                "codigo": "INT-TEST-001",
                "nombre": "Integration Test Project",
                "cliente": "Integration Test Client",
                "presupuesto_total": 75000.00
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["codigo"] == "INT-TEST-001"
    
    def test_list_projects(self, client, admin_headers, sample_projects):
        """Test GET /proyectos"""
        response = client.get(
            "/api/v1/proyectos?page=1&page_size=10",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 3
    
    def test_get_project_by_id(self, client, admin_headers, sample_project):
        """Test GET /proyectos/{id}"""
        response = client.get(
            f"/api/v1/proyectos/{sample_project.id}",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_project.id
        assert data["codigo"] == sample_project.codigo
    
    def test_update_project(self, client, admin_headers, sample_project):
        """Test PUT /proyectos/{id}"""
        response = client.put(
            f"/api/v1/proyectos/{sample_project.id}",
            headers=admin_headers,
            json={
                "nombre": "Updated Project Name",
                "estado": "completado"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nombre"] == "Updated Project Name"
    
    def test_delete_project(self, client, admin_headers, sample_project):
        """Test DELETE /proyectos/{id}"""
        response = client.delete(
            f"/api/v1/proyectos/{sample_project.id}",
            headers=admin_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify deletion
        response = client.get(
            f"/api/v1/proyectos/{sample_project.id}",
            headers=admin_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
```

---

## Step 5: Running Tests

### Run all tests
```bash
cd /home/rolando/Desarrollo/Mark-I/backend
pytest
```

### Run specific test file
```bash
pytest tests/unit/test_auth_services.py -v
```

### Run by marker
```bash
pytest -m unit                    # Run unit tests only
pytest -m integration            # Run integration tests only
pytest -m auth                   # Run auth-related tests
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Run single test
```bash
pytest tests/unit/test_auth_services.py::TestAuthService::test_register_success -v
```

---

## Step 6: Next Steps

1. Create test files for `costos` module
2. Add E2E tests for complete workflows
3. Add performance/load tests
4. Set up CI/CD pipeline with GitHub Actions
5. Configure pre-commit hooks for test execution

---

## Useful Testing Commands

```bash
# Watch mode (re-run tests on file changes)
ptw

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l

# Run slow tests
pytest -m slow

# Show slowest tests
pytest --durations=10

# Run tests in parallel (install pytest-xdist)
pytest -n auto

# Run with verbose output and long summaries
pytest -vv --tb=long
```

---

## Coverage Goals

| Component | Target |
|-----------|--------|
| Services  | 90%+   |
| Routes    | 80%+   |
| Models    | 70%+   |
| Overall   | 80%+   |

Current coverage: 0% (no tests yet)
