# Mark-I Backend - Comprehensive Analysis

## Executive Summary

The Mark-I backend is a **FastAPI-based REST API** for managing construction projects, costs, and expenses. The project follows a clean architecture with modular design, separating concerns into routes, services, repositories, models, and schemas.

**Current Status:** MVP Phase 1 - Basic functionality for projects and expenses management  
**Framework:** FastAPI 0.104.1  
**Database:** SQLite (development) / PostgreSQL (production)  
**Testing Framework:** Pytest 7.4.3 (installed but not yet implemented)

---

## 1. Framework: FastAPI

### Why FastAPI?

- **Modern & Fast:** Built on Starlette, achieves excellent performance
- **Automatic API Documentation:** Swagger UI and ReDoc at `/api/v1/docs`
- **Type Safety:** Full Python type hints support via Pydantic
- **Async-ready:** Native async/await support for concurrent operations
- **Built-in Validation:** Pydantic models provide automatic request/response validation

### Key FastAPI Components Used

```
app/main.py           - Entry point, middleware setup, router registration
app/config.py         - Pydantic Settings for configuration management
app/database.py       - SQLAlchemy ORM setup and session management
app/shared/           - Dependencies, authentication, storage abstraction
app/modules/          - Modular API endpoints (auth, proyectos, costos)
```

---

## 2. Project Structure Overview

```
backend/
├── app/
│   ├── main.py                          # FastAPI app initialization
│   ├── config.py                        # Configuration via Pydantic Settings
│   ├── database.py                      # SQLAlchemy ORM setup
│   ├── modules/                         # Business modules
│   │   ├── auth/                        # Authentication & authorization
│   │   │   ├── models.py               # SQLAlchemy models (Usuario, RolUsuario)
│   │   │   ├── schemas.py              # Pydantic schemas for API
│   │   │   ├── routes.py               # FastAPI endpoints
│   │   │   ├── services.py             # Business logic
│   │   │   ├── repository.py           # Data access layer
│   │   │   └── utils.py                # JWT, password hashing utilities
│   │   ├── proyectos/                  # Project management
│   │   │   ├── models.py               # Proyecto, EstadoProyecto
│   │   │   ├── schemas.py              # Project DTOs
│   │   │   ├── routes.py               # CRUD endpoints
│   │   │   ├── services.py             # Project business logic
│   │   │   └── repository.py           # Database queries
│   │   ├── costos/                     # Expense management
│   │   │   ├── models.py               # Costo, CategoriaGasto, MetodoCaptura
│   │   │   ├── schemas.py              # Expense DTOs
│   │   │   ├── routes.py               # CRUD + file upload endpoints
│   │   │   ├── services.py             # Expense business logic
│   │   │   └── repository.py           # Database queries
│   │   ├── personal/                   # (Phase 2) Personnel management
│   │   ├── tareas/                     # (Phase 2) Task management
│   │   └── horas/                      # (Phase 2) Time tracking
│   ├── shared/
│   │   ├── dependencies.py             # FastAPI dependency injection
│   │   ├── storage.py                  # File storage abstraction (local/MinIO)
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/                              # Test directory (currently empty)
│   └── __init__.py
├── migrations/                         # Alembic database migrations (Planned)
├── requirements.txt                    # Python dependencies
├── .env                               # Environment variables (git-ignored)
├── .env.example                       # Example environment file
└── README.md                          # Project documentation
```

### Architecture Pattern: Repository + Service Pattern

```
Route (FastAPI endpoint)
    ↓
Service (Business Logic)
    ↓
Repository (Data Access)
    ↓
SQLAlchemy Model / Database
```

This ensures:
- Testability (mock repositories in services)
- Separation of concerns
- Reusable business logic
- Clean data access layer

---

## 3. Dependencies Analysis

### Core Dependencies

```
# FastAPI & Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0          # ASGI server
python-multipart==0.0.6             # Form data parsing
pydantic==2.5.0
pydantic-settings==2.1.0            # Configuration management
email-validator==2.1.0              # Email validation

# Database
sqlalchemy==2.0.23                  # ORM
alembic==1.12.1                     # Database migrations
aiosqlite==0.19.0                   # Async SQLite driver
psycopg2-binary==2.9.9             # PostgreSQL adapter

# Authentication
python-jose[cryptography]==3.3.0   # JWT token generation/validation
bcrypt==4.1.2                       # Password hashing

# File Storage
minio==7.2.0                        # S3-compatible storage (production)

# Telegram Bot Integration (Phase 2)
python-telegram-bot==20.7

# Utilities
python-dotenv==1.0.0               # Environment variable loading
httpx==0.25.2                       # Async HTTP client

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1             # Async test support
pytest-cov==4.1.0                  # Code coverage reporting

# Code Quality
black==23.11.0                      # Code formatting
flake8==6.1.0                       # Linting
isort==5.12.0                       # Import sorting

# Future/Commented Out
# pytesseract, easyocr, openai-whisper (Phase 3 - OCR/Speech)
# celery, redis (Phase 2/3 - Async tasks)
```

---

## 4. API Endpoints - Complete Reference

### Base URL
```
http://localhost:8000
API Prefix: /api/v1
Documentation: /api/v1/docs (Swagger UI)
```

### System Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Root info endpoint | No |
| GET | `/health` | Health check for monitoring | No |

### Authentication Endpoints (`/api/v1/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login and get JWT token | No |
| GET | `/auth/me` | Get current authenticated user | JWT |
| PUT | `/auth/me` | Update own profile | JWT |
| POST | `/auth/me/change-password` | Change password | JWT |
| GET | `/auth/usuarios` | List all users (pagination) | Admin |
| GET | `/auth/usuarios/{usuario_id}` | Get user by ID | Admin |
| PUT | `/auth/usuarios/{usuario_id}` | Update user | Admin |
| DELETE | `/auth/usuarios/{usuario_id}` | Delete user | Admin |

### Proyectos (Projects) Endpoints (`/api/v1/proyectos`)

| Method | Endpoint | Description | Filters |
|--------|----------|-------------|---------|
| GET | `/proyectos` | List projects (paginated) | estado, cliente, search |
| POST | `/proyectos` | Create new project | - |
| GET | `/proyectos/{proyecto_id}` | Get project details | - |
| GET | `/proyectos/codigo/{codigo}` | Get project by code | - |
| PUT | `/proyectos/{proyecto_id}` | Update project | - |
| DELETE | `/proyectos/{proyecto_id}` | Delete project | - |
| GET | `/proyectos/{proyecto_id}/resumen` | Get financial summary | - |
| GET | `/proyectos/stats/general` | Statistics (count by state) | - |

**Query Parameters:**
- `page` (default: 1) - Page number
- `page_size` (default: 50, max: 100) - Results per page
- `estado` - Filter by project state
- `cliente` - Filter by client name (partial match)
- `search` - Search in code, name, client, description

### Costos (Expenses) Endpoints (`/api/v1/costos`)

| Method | Endpoint | Description | Filters |
|--------|----------|-------------|---------|
| GET | `/costos` | List expenses (paginated) | proyecto_id, categoria, fecha, validado, con_factura, search |
| POST | `/costos` | Create new expense | - |
| GET | `/costos/{costo_id}` | Get expense details | - |
| PUT | `/costos/{costo_id}` | Update expense | - |
| DELETE | `/costos/{costo_id}` | Delete expense | - |
| POST | `/costos/{costo_id}/factura` | Upload invoice file | - |
| POST | `/costos/{costo_id}/validar` | Validate/reject expense | - |
| GET | `/costos/proyecto/{proyecto_id}/total` | Get project total spending | - |
| GET | `/costos/stats/general` | Expense statistics | periodo |

**Query Parameters:**
- `page` (default: 1)
- `page_size` (default: 50, max: 100)
- `proyecto_id` - Filter by project
- `categoria` - Filter by expense category
- `fecha_desde`, `fecha_hasta` - Date range filter
- `validado` - Filter by validation status
- `con_factura` - Filter by invoice presence
- `search` - Search in description and provider
- `periodo` - Statistics period (hoy, semana, mes, año, todos)

---

## 5. Data Models

### Auth Module

#### Usuario (User)
```python
- id: str (UUID)                    # Primary key
- username: str                     # Unique, indexed
- email: str                        # Unique, indexed
- hashed_password: str              # bcrypt hashed
- nombre_completo: str
- telefono: str (optional)
- telegram_id: str (optional)       # For bot integration
- telegram_username: str (optional)
- rol: RolUsuario enum              # admin, gerente, supervisor, trabajador
- activo: bool                      # Active status
- puede_validar_gastos: bool (property)
- es_admin: bool (property)
- creado_en: datetime
- actualizado_en: datetime
- ultimo_acceso: datetime (optional)
```

#### RolUsuario (User Roles)
```
- ADMIN:       Full system access
- GERENTE:     Project and expense validation
- SUPERVISOR:  Expense validation and hour tracking
- TRABAJADOR:  Report expenses and view tasks
```

---

### Proyectos Module

#### Proyecto (Project)
```python
- id: str (UUID)                    # Primary key
- codigo: str                       # Unique project code (e.g., CASA-001)
- nombre: str                       # Project name
- cliente: str                      # Client name
- descripcion: str (optional)
- fecha_inicio: datetime (optional)
- fecha_fin_estimada: datetime (optional)
- fecha_fin_real: datetime (optional)
- presupuesto_total: Decimal       # Total budget
- horas_presupuestadas: Decimal (optional)
- estado: EstadoProyecto enum      # See below
- datos_adicionales: JSON (optional) # Flexible metadata
- creado_en: datetime
- actualizado_en: datetime
- dias_transcurridos: int (property)
- dias_restantes: int (property)
```

#### EstadoProyecto (Project States)
```
- PROSPECTO:   Initial prospecting state
- COTIZACION:  Quotation stage
- APROBADO:    Approved by client
- EN_PROGRESO: Currently active
- PAUSADO:     Temporarily paused
- COMPLETADO:  Finished
- CANCELADO:   Cancelled
```

---

### Costos Module

#### Costo (Expense)
```python
- id: str (UUID)                    # Primary key
- proyecto_id: str (FK)             # Foreign key to Proyecto
- categoria: CategoriaGasto enum    # Expense category
- monto: Decimal                    # Expense amount
- descripcion: str                  # Detailed description
- proveedor_nombre: str (optional)  # Supplier name
- factura_url: str (optional)       # Uploaded invoice path
- factura_filename: str (optional)  # Original filename
- fecha_gasto: datetime             # When expense occurred
- metodo_captura: MetodoCaptura enum # How it was recorded
- validado: bool                    # Validation status
- validado_por: str (optional)      # ID of validator
- validado_en: datetime (optional)  # When it was validated
- notas_validacion: str (optional)  # Validation notes
- creado_en: datetime
- actualizado_en: datetime
- tiene_factura: bool (property)
- dias_desde_gasto: int (property)
```

#### CategoriaGasto (Expense Categories)
```
- MATERIALES:   Building materials
- MANO_OBRA:    Labor costs
- TRANSPORTE:   Transportation
- HERRAMIENTAS: Tools
- SUBCONTRATO:  Subcontractor work
- PERMISOS:     Permits and licenses
- SERVICIOS:    Services
- OTROS:        Other expenses
```

#### MetodoCaptura (Capture Methods)
```
- MANUAL_WEB:  Web form entry
- MANUAL_BOT:  Telegram bot entry
- FOTO_BOT:    Photo via bot (OCR pending)
- OCR_AUTO:    Automatic OCR extraction
- VOZ:         Voice recording (pending)
- API:         API integration
```

---

## 6. Authentication & Authorization

### JWT Token Flow

```
1. User calls POST /api/v1/auth/login with username/email and password
2. Service validates credentials against bcrypt hash
3. On success, JWT token is generated with:
   - sub (subject): user ID
   - username: username
   - rol: user role (as string)
   - exp: expiration time (30 minutes by default)
4. Token is returned in TokenResponse
5. Client includes token in Authorization header: Bearer <token>
6. FastAPI dependency validates token on protected routes
```

### Security Implementation

```python
# Location: app/modules/auth/utils.py
hash_password(password)         # bcrypt hashing
verify_password(plain, hashed)  # bcrypt verification
create_access_token(data)       # JWT generation
validate_token(token)           # JWT validation

# Location: app/shared/dependencies.py
get_current_user()              # Extract user from token
get_current_active_user()       # Ensure user is active
require_admin()                 # Role-based access control
require_gerente_or_admin()      # Multi-role check
can_validate_expenses()         # Permission check
```

### Role-Based Access Control (RBAC)

```
Admin:
  - Full access to all endpoints
  - User management
  - Expense validation
  - Project management

Gerente:
  - Project management
  - Expense validation
  - View statistics

Supervisor:
  - Expense validation
  - Time tracking
  - View assigned projects

Trabajador:
  - Report expenses
  - View assigned tasks
  - Limited project visibility
```

---

## 7. File Storage Architecture

### Abstraction Layer: `app/shared/storage.py`

The project implements a **Strategy Pattern** for file storage:

```python
StorageService (Abstract Interface)
├── LocalFileStorage
│   └── Files stored in ./uploads directory
│   └── URLs: /uploads/{relative_path}
└── MinIOStorage
    └── S3-compatible object storage
    └── Pre-signed URLs valid for 7 days
```

### Usage in Costos Module

```python
@router.post("/{costo_id}/factura")
async def upload_factura(
    costo_id: str,
    file: UploadFile = File(...),
    service: CostoService = Depends(get_costo_service)
):
    return service.upload_factura(costo_id, file, storage_service)
```

### Configuration

```env
# Local Storage (Development)
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# MinIO (Production)
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=obras-facturas
MINIO_SECURE=False
```

---

## 8. Database Configuration

### Supported Databases

#### Development: SQLite
```
DATABASE_URL=sqlite:///./obras.db
- File-based database
- No additional setup required
- Limited concurrent connections
- Perfect for development and testing
```

#### Production: PostgreSQL
```
DATABASE_URL=postgresql://user:pass@localhost:5432/obras
- Enterprise-grade relational database
- Better concurrent handling
- ACID compliance
- Scalable
```

### SQLAlchemy Setup

```python
# Location: app/database.py
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={...},        # SQLite: check_same_thread=False
    pool_pre_ping=True,        # Verify connections
    echo=settings.DEBUG        # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()      # Base class for all models

# Dependency for routes
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Database Initialization

```bash
# Development: Auto-create tables (in main.py when DEBUG=True)
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

# Production: Use Alembic migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

---

## 9. Testing Framework Setup

### Current Status: **NOT YET IMPLEMENTED**

The `pytest` framework is installed with supporting packages but no tests exist yet.

### Installed Testing Dependencies

```
pytest==7.4.3                  # Test runner
pytest-asyncio==0.21.1        # Async test support
pytest-cov==4.1.0            # Coverage reporting
httpx==0.25.2                # Async HTTP client for endpoint testing
```

### Recommended Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── __init__.py
├── unit/
│   ├── test_auth_services.py     # AuthService business logic tests
│   ├── test_proyecto_services.py
│   ├── test_costo_services.py
│   └── test_repositories.py      # Repository layer tests
├── integration/
│   ├── test_auth_routes.py       # Complete auth flow tests
│   ├── test_proyectos_routes.py  # Project CRUD endpoint tests
│   ├── test_costos_routes.py     # Expense endpoint tests
│   ├── test_file_upload.py       # File upload scenarios
│   └── test_permissions.py       # RBAC tests
├── fixtures/
│   ├── users.py               # Sample user data
│   ├── projects.py            # Sample project data
│   └── expenses.py            # Sample expense data
└── e2e/
    └── test_project_workflow.py   # Full workflow scenarios
```

---

## 10. Recommendations for Comprehensive Testing

### 1. Setup Testing Infrastructure

**Create `conftest.py` for shared fixtures:**
```python
@pytest.fixture
def db_session():
    """Provide test database session"""
    # Use in-memory SQLite for tests
    
@pytest.fixture
def client():
    """Provide FastAPI TestClient"""
    return TestClient(app)

@pytest.fixture
def admin_user():
    """Provide admin test user"""
    
@pytest.fixture
def normal_user():
    """Provide normal test user"""
    
@pytest.fixture
def sample_project():
    """Provide sample project data"""
    
@pytest.fixture
def sample_expense():
    """Provide sample expense data"""
```

### 2. Unit Tests

Focus on business logic in services:

- **AuthService tests**
  - User registration validation
  - Password hashing verification
  - JWT token generation
  - Login with valid/invalid credentials
  - Token expiration handling

- **ProyectoService tests**
  - Project creation with validation
  - Budget calculations
  - State transitions
  - Search and filtering logic
  - Financial summaries

- **CostoService tests**
  - Expense creation
  - Validation workflow
  - Category validation
  - File upload handling
  - Statistics calculation

### 3. Integration Tests

Test endpoints with full request/response cycle:

- **Authentication**
  - POST /auth/register (success, duplicates, validation errors)
  - POST /auth/login (valid/invalid credentials)
  - GET /auth/me (with/without token)
  - Protected endpoints return 401 without token

- **CRUD Operations**
  - Complete CRUD cycles for projects and expenses
  - Pagination and filtering
  - Search functionality
  - Date range filters

- **File Operations**
  - File upload and storage
  - File retrieval
  - File deletion
  - Large file handling
  - Invalid file types rejection

- **Permissions**
  - Admin-only endpoints
  - Role-based restrictions
  - User can't modify others' data

### 4. Test Coverage Goals

```bash
# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Target coverage:
- Services: 90%+
- Routes: 80%+
- Models: 70%+
- Overall: 80%+
```

### 5. Testing Best Practices

```python
# Use async support
@pytest.mark.asyncio
async def test_async_endpoint():
    pass

# Test edge cases
def test_create_project_with_zero_budget():
    # Should raise validation error

# Test error responses
def test_login_with_wrong_password():
    response = client.post(...)
    assert response.status_code == 401

# Mock external services
@patch('app.shared.storage.storage_service.upload_file')
def test_expense_upload(mock_upload):
    pass

# Use factories for test data
def test_with_multiple_users(user_factory):
    user1 = user_factory(rol=RolUsuario.ADMIN)
    user2 = user_factory(rol=RolUsuario.TRABAJADOR)
```

### 6. Pytest Configuration

Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
```

### 7. GitHub Actions CI/CD Template

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
```

---

## 11. Configuration Management

### Environment Variables (`.env`)

```env
# Application Settings
ENVIRONMENT=development           # development, staging, production
APP_NAME="Mark-I - Sistema de Gestión de Obras"
APP_VERSION=1.0.0
DEBUG=True
API_V1_PREFIX=/api/v1

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./obras.db

# Security (CHANGE IN PRODUCTION)
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Storage
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Features (Phase 2/3)
TELEGRAM_BOT_TOKEN=<optional>
OCR_ENGINE=<optional>
STT_ENGINE=<optional>
CELERY_BROKER_URL=<optional>
REDIS_URL=<optional>
```

### Using Configuration

```python
from app.config import settings

# Single instance with caching
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Usage
settings = get_settings()
print(settings.APP_NAME)
print(settings.allowed_origins_list)  # Converts comma-separated to list
```

---

## 12. Development Workflow

### Quick Start

```bash
# 1. Virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start development server
uvicorn app.main:app --reload

# 5. Access API
# Swagger UI: http://localhost:8000/api/v1/docs
# ReDoc: http://localhost:8000/api/v1/redoc
```

### Code Quality

```bash
# Format code
black app/

# Check linting
flake8 app/

# Sort imports
isort app/

# Run all checks
black app/ && flake8 app/ && isort app/
```

### Database Management

```bash
# Initialize (development)
# Automatic with DEBUG=True in main.py

# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_auth_services.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/unit/test_auth_services.py::test_register_success
```

---

## 13. Phase Roadmap

### Phase 1 (Current - MVP)
- Basic project management (CRUD)
- Expense tracking with file uploads
- User authentication with JWT
- Role-based access control
- SQLite database support
- Local file storage

### Phase 2
- Task management module
- Time tracking (hours)
- Personnel management
- Telegram bot integration
- Background job queue (Celery)
- Redis caching

### Phase 3
- OCR for invoice processing
- Speech-to-text expense recording
- Advanced analytics
- Budget forecasting
- Report generation

### Phase 4
- Multi-tenancy support
- Redis implementation
- Advanced caching strategies
- Real-time notifications via WebSockets

---

## 14. API Response Format

All endpoints follow a consistent response pattern:

### Successful Response

```json
{
  "id": "uuid",
  "campo1": "valor1",
  "campo2": 123,
  "creado_en": "2024-01-15T10:30:00",
  "actualizado_en": "2024-01-15T10:30:00"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### List Response

```json
{
  "total": 150,
  "items": [...],
  "page": 1,
  "page_size": 50
}
```

### Expenses List Response

```json
{
  "total": 50,
  "total_monto": 15000.50,
  "items": [...],
  "page": 1,
  "page_size": 50
}
```

---

## 15. Common Development Issues & Solutions

### SQLite Limitations
- **Issue:** "Database locked" error with concurrent requests
- **Solution:** Use PostgreSQL for production

### JWT Token Issues
- **Issue:** "Token invalid" or "Token expired"
- **Solution:** Check SECRET_KEY is consistent, verify token format

### CORS Errors
- **Issue:** Frontend can't call backend API
- **Solution:** Add frontend domain to ALLOWED_ORIGINS in .env

### File Upload Issues
- **Issue:** Files not saving or permissions denied
- **Solution:** Ensure ./uploads directory exists with write permissions

### Database Migrations
- **Issue:** Schema mismatch between code and database
- **Solution:** Run `alembic upgrade head` to apply pending migrations

---

## 16. Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `app/main.py` | FastAPI app setup | 105 |
| `app/config.py` | Configuration management | 93 |
| `app/database.py` | Database setup | 71 |
| `app/modules/auth/models.py` | User model | 67 |
| `app/modules/auth/routes.py` | Auth endpoints | 250 |
| `app/modules/auth/services.py` | Auth logic | 150+ |
| `app/modules/proyectos/models.py` | Project model | 85 |
| `app/modules/proyectos/routes.py` | Project endpoints | 206 |
| `app/modules/costos/models.py` | Expense model | 96 |
| `app/modules/costos/routes.py` | Expense endpoints | 248 |
| `app/shared/dependencies.py` | Auth dependencies | 145 |
| `app/shared/storage.py` | Storage abstraction | 206 |

---

## 17. Quick Statistics

```
Framework:              FastAPI 0.104.1
Python Version:         3.11+ (inferred)
Database:              SQLite (dev) / PostgreSQL (prod)
Authentication:        JWT (30 min expiry)
Core Dependencies:     15 installed
Testing Framework:     Pytest (configured, not used yet)
Code Quality Tools:    Black, Flake8, isort
Lines of Backend Code: ~2000+ (excluding tests)
API Endpoints:         30+ active endpoints
Database Models:       3 (Usuario, Proyecto, Costo)
Modules:              3 active (auth, proyectos, costos)
Modular Layers:       Routes → Services → Repository → Models
```

---

## Summary

The Mark-I backend is a well-architected, production-ready FastAPI application with:

✅ Clean separation of concerns (routes, services, repositories)
✅ Comprehensive authentication with JWT and role-based access control
✅ Flexible file storage abstraction (local and MinIO)
✅ Type-safe with Pydantic validation
✅ Database agnostic (SQLite or PostgreSQL)
✅ Fully documented endpoints via Swagger UI

⚠️ Testing infrastructure is installed but not yet implemented
⚠️ Database migrations (Alembic) configured but not yet used
⚠️ Future phases require additional modules and services

