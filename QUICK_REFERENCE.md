# Mark-I Backend - Quick Reference Card

**Status:** Fase 1 ✅ | Fase 2 ✅ | ~74 endpoints activos

## Framework & Tech Stack
- **Framework:** FastAPI 0.104.1 (modern, async-capable, auto-docs)
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Authentication:** JWT with bcrypt password hashing
- **Storage:** Local filesystem or MinIO (S3-compatible)
- **Bot:** Telegram Bot ✅ (8 comandos)
- **Testing:** Pytest (installed, 0% coverage - implement immediately)

---

## Start Development Server

```bash
cd backend/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**Access API:** http://localhost:8000
**Swagger UI:** http://localhost:8000/api/v1/docs
**ReDoc:** http://localhost:8000/api/v1/redoc

---

## All API Endpoints at a Glance

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| **SYSTEM** |||
| GET | `/` | Root info | No |
| GET | `/health` | Health check | No |
| **AUTH** |||
| POST | `/api/v1/auth/register` | Register user | No |
| POST | `/api/v1/auth/login` | Login & get JWT | No |
| GET | `/api/v1/auth/me` | Current user | JWT |
| PUT | `/api/v1/auth/me` | Update profile | JWT |
| POST | `/api/v1/auth/me/change-password` | Change pwd | JWT |
| GET | `/api/v1/auth/usuarios` | List users | Admin |
| GET | `/api/v1/auth/usuarios/{id}` | Get user | Admin |
| PUT | `/api/v1/auth/usuarios/{id}` | Update user | Admin |
| DELETE | `/api/v1/auth/usuarios/{id}` | Delete user | Admin |
| **PROJECTS** |||
| GET | `/api/v1/proyectos` | List projects | JWT |
| POST | `/api/v1/proyectos` | Create project | JWT |
| GET | `/api/v1/proyectos/{id}` | Get project | JWT |
| GET | `/api/v1/proyectos/codigo/{code}` | Get by code | JWT |
| PUT | `/api/v1/proyectos/{id}` | Update project | JWT |
| DELETE | `/api/v1/proyectos/{id}` | Delete project | JWT |
| GET | `/api/v1/proyectos/{id}/resumen` | Summary | JWT |
| GET | `/api/v1/proyectos/stats/general` | Stats | JWT |
| **EXPENSES** |||
| GET | `/api/v1/costos` | List expenses | JWT |
| POST | `/api/v1/costos` | Create expense | JWT |
| GET | `/api/v1/costos/{id}` | Get expense | JWT |
| PUT | `/api/v1/costos/{id}` | Update expense | JWT |
| DELETE | `/api/v1/costos/{id}` | Delete expense | JWT |
| POST | `/api/v1/costos/{id}/factura` | Upload invoice | JWT |
| POST | `/api/v1/costos/{id}/validar` | Validate expense | JWT |
| GET | `/api/v1/costos/proyecto/{id}/total` | Project total | JWT |
| GET | `/api/v1/costos/stats/general` | Stats | JWT |
| **TASKS** ✨ NEW |||
| GET | `/api/v1/tareas` | List tasks | JWT |
| POST | `/api/v1/tareas` | Create task | JWT |
| GET | `/api/v1/tareas/{id}` | Get task | JWT |
| PUT | `/api/v1/tareas/{id}` | Update task | JWT |
| DELETE | `/api/v1/tareas/{id}` | Delete task | JWT |
| PATCH | `/api/v1/tareas/{id}/estado` | Change status | JWT |
| PATCH | `/api/v1/tareas/{id}/asignar` | Assign employee | JWT |
| GET | `/api/v1/tareas/proyecto/{id}` | By project | JWT |
| GET | `/api/v1/tareas/empleado/{id}` | By employee | JWT |
| GET | `/api/v1/tareas/hoy` | Today's tasks | JWT |
| GET | `/api/v1/tareas/semana` | Week's tasks | JWT |
| **PERSONNEL** ✨ NEW |||
| GET | `/api/v1/personal` | List employees | JWT |
| POST | `/api/v1/personal` | Create employee | JWT |
| GET | `/api/v1/personal/{id}` | Get employee | JWT |
| PUT | `/api/v1/personal/{id}` | Update employee | JWT |
| DELETE | `/api/v1/personal/{id}` | Delete employee | JWT |
| GET | `/api/v1/personal/{id}/horas` | Hours worked | JWT |
| GET | `/api/v1/personal/{id}/proyectos` | Assigned projects | JWT |
| **HOURS** ✨ NEW |||
| GET | `/api/v1/horas` | List records | JWT |
| POST | `/api/v1/horas` | Register hours | JWT |
| GET | `/api/v1/horas/{id}` | Get record | JWT |
| PUT | `/api/v1/horas/{id}` | Update record | JWT |
| DELETE | `/api/v1/horas/{id}` | Delete record | JWT |
| GET | `/api/v1/horas/empleado/{id}` | By employee | JWT |
| GET | `/api/v1/horas/proyecto/{id}` | By project | JWT |
| GET | `/api/v1/horas/empleado/{e}/proyecto/{p}` | Specific | JWT |
| GET | `/api/v1/horas/stats/general` | Statistics | JWT |
| POST | `/api/v1/horas/calcular-mano-obra` | Labor cost | JWT |
| **NOTIFICATIONS** ✨ NEW |||
| GET | `/api/v1/notificaciones` | List notifications | JWT |
| POST | `/api/v1/notificaciones` | Create notification | JWT |
| GET | `/api/v1/notificaciones/{id}` | Get notification | JWT |
| PUT | `/api/v1/notificaciones/{id}` | Update notification | JWT |
| DELETE | `/api/v1/notificaciones/{id}` | Delete notification | JWT |
| PATCH | `/api/v1/notificaciones/{id}/marcar-leida` | Mark as read | JWT |
| GET | `/api/v1/notificaciones/no-leidas` | Unread | JWT |
| GET | `/api/v1/notificaciones/usuario/{id}` | By user | JWT |
| GET | `/api/v1/notificaciones/proyecto/{id}` | By project | JWT |
| POST | `/api/v1/notificaciones/marcar-todas-leidas` | Mark all read | JWT |

**TOTAL: ~74 endpoints**

---

## User Roles & Permissions

```
ADMIN
  - Full access to everything
  - User management
  - All expense validation
  - All project management

GERENTE
  - Project & expense management
  - Expense validation
  - Statistics viewing

SUPERVISOR
  - Expense validation
  - Time tracking
  - Assigned project viewing

TRABAJADOR
  - Expense reporting
  - Task viewing
  - Limited project access
```

---

## Common cURL Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure123",
    "nombre_completo": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "secure123"
  }'
```

### Create Project
```bash
curl -X POST http://localhost:8000/api/v1/proyectos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "PROJ-001",
    "nombre": "New Project",
    "cliente": "Client Name",
    "presupuesto_total": 100000.00
  }'
```

### List Projects with Filters
```bash
curl -X GET 'http://localhost:8000/api/v1/proyectos?estado=en_progreso&page=1&page_size=10' \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Expense
```bash
curl -X POST http://localhost:8000/api/v1/costos \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "proyecto_id": "project-uuid",
    "categoria": "materiales",
    "monto": 1500.00,
    "descripcion": "Building materials",
    "proveedor_nombre": "ABC Hardware"
  }'
```

### Upload Invoice
```bash
curl -X POST http://localhost:8000/api/v1/costos/expense-uuid/factura \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@invoice.pdf"
```

---

## Data Models Summary

### Usuario (User)
- **Fields:** id, username, email, password_hash, nombre_completo, telefono, telegram_id, rol, activo, creado_en, actualizado_en, ultimo_acceso
- **Roles:** ADMIN, GERENTE, SUPERVISOR, TRABAJADOR
- **Key Fields:** username (unique), email (unique), rol (enum), activo (bool)

### Proyecto (Project)
- **Fields:** id, codigo, nombre, cliente, descripcion, fecha_inicio, fecha_fin_estimada, fecha_fin_real, presupuesto_total, horas_presupuestadas, estado, datos_adicionales (JSON), creado_en, actualizado_en
- **States:** PROSPECTO, COTIZACION, APROBADO, EN_PROGRESO, PAUSADO, COMPLETADO, CANCELADO
- **Key Fields:** codigo (unique), presupuesto_total, estado (enum)

### Costo (Expense)
- **Fields:** id, proyecto_id (FK), categoria, monto, descripcion, proveedor_nombre, factura_url, factura_filename, fecha_gasto, metodo_captura, validado, validado_por, validado_en, notas_validacion, creado_en, actualizado_en
- **Categories:** MATERIALES, MANO_OBRA, TRANSPORTE, HERRAMIENTAS, SUBCONTRATO, PERMISOS, SERVICIOS, OTROS
- **Capture Methods:** MANUAL_WEB, MANUAL_BOT, FOTO_BOT, OCR_AUTO, VOZ, API
- **Key Fields:** monto (decimal), validado (bool), factura_url (optional)

### Tarea (Task) ✨ NEW
- **Fields:** id, proyecto_id (FK), titulo, descripcion, fecha_programada, prioridad, estado, asignado_a (FK), creado_por (FK), creado_en, actualizado_en
- **States:** PENDIENTE, EN_PROGRESO, COMPLETADA, CANCELADA
- **Priorities:** ALTA, MEDIA, BAJA
- **Key Fields:** titulo, estado (enum), prioridad (enum), asignado_a

### Personal (Employee) ✨ NEW
- **Fields:** id, nombre, telefono, email, especialidad, costo_hora, activo, creado_en, actualizado_en
- **Key Fields:** nombre, costo_hora (decimal), activo (bool), especialidad

### RegistroHoras (Hour Record) ✨ NEW
- **Fields:** id, empleado_id (FK), proyecto_id (FK), horas, fecha, descripcion, registrado_por (FK), creado_en
- **Key Fields:** horas (decimal), fecha, empleado_id, proyecto_id

### Notificacion (Notification) ✨ NEW
- **Fields:** id, usuario_id (FK), proyecto_id (FK), tipo, titulo, mensaje, leida, fecha_leida, creado_en
- **Types:** INFO, ADVERTENCIA, ERROR, EXITO
- **Key Fields:** tipo (enum), titulo, mensaje, leida (bool)

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Pydantic settings
│   ├── database.py              # SQLAlchemy setup
│   ├── modules/
│   │   ├── auth/                # Users & authentication
│   │   │   ├── models.py        # Usuario, RolUsuario
│   │   │   ├── schemas.py       # Pydantic DTOs
│   │   │   ├── routes.py        # 9 endpoints
│   │   │   ├── services.py      # Business logic
│   │   │   ├── repository.py    # Data access
│   │   │   └── utils.py         # JWT, bcrypt helpers
│   │   ├── proyectos/           # Project management
│   │   │   ├── models.py        # Proyecto, EstadoProyecto
│   │   │   ├── routes.py        # 8 endpoints
│   │   │   ├── services.py
│   │   │   └── repository.py
│   │   ├── costos/              # Expense tracking
│   │   │   ├── models.py        # Costo, CategoriaGasto
│   │   │   ├── routes.py        # 9 endpoints
│   │   │   ├── services.py
│   │   │   └── repository.py
│   │   ├── tareas/              # Task management ✨ NEW
│   │   │   ├── models.py        # Tarea, EstadoTarea, PrioridadTarea
│   │   │   ├── routes.py        # 11 endpoints
│   │   │   ├── services.py
│   │   │   └── repository.py
│   │   ├── personal/            # Personnel management ✨ NEW
│   │   │   ├── models.py        # Personal
│   │   │   ├── routes.py        # 7 endpoints
│   │   │   ├── services.py
│   │   │   └── repository.py
│   │   ├── horas/               # Hours tracking ✨ NEW
│   │   │   ├── models.py        # RegistroHoras
│   │   │   ├── routes.py        # 10 endpoints
│   │   │   ├── services.py
│   │   │   └── repository.py
│   │   └── notificaciones/      # Notifications ✨ NEW
│   │       ├── models.py        # Notificacion, TipoNotificacion
│   │       ├── routes.py        # 10 endpoints
│   │       ├── services.py
│   │       └── repository.py
│   └── shared/
│       ├── dependencies.py      # Auth dependency injection
│       └── storage.py           # File storage abstraction
├── bot/                         # Telegram Bot ✨ NEW
│   ├── main.py                  # Bot entry point
│   ├── handlers/                # Command handlers
│   ├── keyboards.py             # Telegram keyboards
│   └── api_client.py            # API communication
├── tests/                       # EMPTY - needs implementation!
├── migrations/                  # Alembic migrations (not yet used)
├── scripts/                     # Utility scripts
│   └── seed_data.py            # Database seeding
├── requirements.txt
├── .env.example
└── README.md
```

---

## Configuration (.env)

```env
# Core
ENVIRONMENT=development
APP_NAME="Mark-I - Sistema de Gestión de Obras"
APP_VERSION=1.0.0
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./obras.db
# Or for production: postgresql://user:pass@host/obras

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Storage
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# Optional
TELEGRAM_BOT_TOKEN=<optional>
OCR_ENGINE=<optional>
STT_ENGINE=<optional>
```

---

## Code Quality Commands

```bash
# Format code
black app/

# Check linting
flake8 app/

# Sort imports
isort app/

# All checks
black app/ && flake8 app/ && isort app/
```

---

## Testing Setup (TODO - CRITICAL)

**Current Status:** 0% test coverage (NEEDS IMPLEMENTATION)

See `TESTING_SETUP.md` for detailed setup instructions.

Quick start:
```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/unit/test_auth_services.py -v
```

---

## Response Format

### Success Response
```json
{
  "id": "uuid",
  "field1": "value1",
  "creado_en": "2024-01-15T10:30:00",
  "actualizado_en": "2024-01-15T10:30:00"
}
```

### List Response
```json
{
  "total": 100,
  "items": [...],
  "page": 1,
  "page_size": 50
}
```

### Error Response
```json
{
  "detail": "Error message describing the problem"
}
```

---

## HTTP Status Codes

- **200 OK** - Successful GET, PUT, DELETE
- **201 Created** - Successful POST
- **400 Bad Request** - Validation error
- **401 Unauthorized** - Missing/invalid JWT token
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource doesn't exist
- **500 Internal Error** - Server error

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Database locked" | Use PostgreSQL for production |
| "Token invalid" | Check SECRET_KEY is set, verify format |
| CORS errors | Add frontend URL to ALLOWED_ORIGINS |
| Files not saving | Ensure ./uploads dir exists with write permissions |
| Import errors | Run `pip install -r requirements.txt` |

---

## Dependencies Summary

**Core (6):** fastapi, uvicorn, pydantic, pydantic-settings, python-multipart, email-validator

**Database (4):** sqlalchemy, alembic, psycopg2-binary, aiosqlite

**Auth (2):** python-jose, bcrypt

**Storage (1):** minio

**Testing (4):** pytest, pytest-asyncio, pytest-cov, httpx

**Code Quality (3):** black, flake8, isort

---

## Architecture Pattern

```
REQUEST
  ↓
FastAPI Route (Request validation via Pydantic)
  ↓
Service (Business logic, validation, orchestration)
  ↓
Repository (Database queries via SQLAlchemy)
  ↓
SQLAlchemy Model / Database
  ↓
RESPONSE (Pydantic schema serialization)
```

---

## Key Files Size Reference

| File | Size | Purpose |
|------|------|---------|
| main.py | 105 lines | FastAPI initialization |
| config.py | 93 lines | Configuration management |
| database.py | 71 lines | Database setup |
| auth/routes.py | 250 lines | 9 auth endpoints |
| proyectos/routes.py | 206 lines | 8 project endpoints |
| costos/routes.py | 248 lines | 8 expense endpoints |
| shared/dependencies.py | 145 lines | Auth dependency injection |
| shared/storage.py | 206 lines | Storage abstraction |

---

## Generated Documentation Files

1. **BACKEND_ANALYSIS.md** (27KB) - Complete technical analysis
2. **API_ENDPOINTS.md** (4.9KB) - Quick endpoint reference
3. **TESTING_SETUP.md** (22KB) - Testing implementation guide
4. **BACKEND_SUMMARY.txt** (18KB) - Executive summary
5. **QUICK_REFERENCE.md** - This file

---

## Deployment Checklist

- [ ] Implement test suite (80%+ coverage)
- [ ] Set up database migrations
- [ ] Configure CI/CD pipeline
- [ ] Set production SECRET_KEY
- [ ] Set production DATABASE_URL (PostgreSQL)
- [ ] Set production STORAGE_TYPE (MinIO)
- [ ] Set ALLOWED_ORIGINS for production domain
- [ ] Enable CORS for production frontend
- [ ] Set DEBUG=False
- [ ] Configure logging/monitoring
- [ ] Security audit
- [ ] Performance testing
- [ ] Load testing

---

## Next Steps

1. **CRITICAL:** Implement comprehensive test suite for Phase 2 modules (see TESTING_SETUP.md)
2. **CRITICAL:** Set up database migrations with Alembic for new models
3. Update seed script with data for Phase 2 modules
4. Configure Telegram Bot token and test all commands
5. Set up CI/CD pipeline
6. Configure monitoring and logging
7. Begin Phase 3: OCR and Speech-to-Text integration

---

## Useful Links

- FastAPI Docs: https://fastapi.tiangolo.com
- Pydantic Docs: https://docs.pydantic.dev
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Pytest Docs: https://docs.pytest.org

---

**Last Updated:** November 9, 2025
**Backend Version:** 2.0.0 (Phase 1 + Phase 2 Complete)
**Status:** Production-ready code, Testing needed for Phase 2 modules

