# Mark-I Backend API

Backend FastAPI para el Sistema de Gestión de Obras y Costos.

**Versión:** 2.0.0 | **Estado:** Fase 1 ✅ + Fase 2 ✅ | **Endpoints:** ~74 activos

## 🚀 Quick Start

### Opción 1: Desarrollo con SQLite (más simple)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar variables de entorno
cp .env.example .env

# 4. Iniciar servidor
uvicorn app.main:app --reload
```

La API estará disponible en: http://localhost:8000

Documentación Swagger: http://localhost:8000/api/v1/docs

### Opción 2: Con Docker (completo con PostgreSQL y MinIO)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

### Opción 3: Docker solo infraestructura (PostgreSQL, Redis, MinIO)

```bash
# Iniciar solo servicios de infraestructura
docker-compose -f docker/docker-compose.dev.yml up -d

# Luego ejecutar backend localmente
cd backend
uvicorn app.main:app --reload
```

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py                 # Entry point de FastAPI
│   ├── config.py              # Configuración
│   ├── database.py            # SQLAlchemy setup
│   ├── modules/               # Módulos de negocio
│   │   ├── auth/             # Autenticación y usuarios (9 endpoints)
│   │   ├── proyectos/        # Gestión de proyectos (8 endpoints)
│   │   ├── costos/           # Gestión de gastos (9 endpoints)
│   │   ├── tareas/           # ✅ Tareas (11 endpoints) - Fase 2
│   │   ├── personal/         # ✅ Personal (7 endpoints) - Fase 2
│   │   ├── horas/            # ✅ Registro de horas (10 endpoints) - Fase 2
│   │   └── notificaciones/   # ✅ Notificaciones (10 endpoints) - Fase 2
│   ├── shared/               # Código compartido
│   │   ├── storage.py       # Abstracción de storage
│   │   └── dependencies.py  # Dependencies de FastAPI
│   └── utils/               # Utilidades
├── bot/                    # ✅ Telegram Bot (8 comandos) - Fase 2
│   ├── main.py            # Entry point del bot
│   ├── handlers/          # Command handlers
│   ├── keyboards.py       # Telegram keyboards
│   └── api_client.py      # API communication
├── tests/                 # Tests (pendiente implementación)
├── migrations/           # Alembic migrations
├── scripts/              # Scripts de utilidad
│   └── seed_data.py     # Seed con datos de Fase 1 + Fase 2
├── requirements.txt     # Dependencias
└── .env                # Variables de entorno
```

## 🔧 Configuración

### Variables de Entorno

Edita el archivo `.env` con tu configuración:

```env
# Database
DATABASE_URL=sqlite:///./obras.db  # O PostgreSQL para producción

# Security
SECRET_KEY=your-super-secret-key-change-this

# Storage
STORAGE_TYPE=local  # O 'minio' para producción
UPLOAD_DIR=./uploads
```

### Migraciones de Base de Datos

```bash
# Crear migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

## 📚 Endpoints Principales

### Autenticación (9 endpoints)

- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión
- `GET /api/v1/auth/me` - Obtener usuario actual
- `PUT /api/v1/auth/me` - Actualizar perfil
- `POST /api/v1/auth/me/change-password` - Cambiar contraseña
- `GET /api/v1/auth/usuarios` - Listar usuarios (Admin)
- Y más...

### Proyectos (8 endpoints)

- `GET /api/v1/proyectos` - Listar proyectos
- `POST /api/v1/proyectos` - Crear proyecto
- `GET /api/v1/proyectos/{id}` - Obtener proyecto
- `PUT /api/v1/proyectos/{id}` - Actualizar proyecto
- `GET /api/v1/proyectos/{id}/resumen` - Resumen financiero
- `GET /api/v1/proyectos/stats/general` - Estadísticas
- Y más...

### Costos/Gastos (9 endpoints)

- `GET /api/v1/costos` - Listar gastos
- `POST /api/v1/costos` - Registrar gasto
- `POST /api/v1/costos/{id}/factura` - Subir factura
- `POST /api/v1/costos/{id}/validar` - Validar gasto
- `GET /api/v1/costos/stats/general` - Estadísticas
- Y más...

### Tareas (11 endpoints) ✨ Fase 2

- `GET /api/v1/tareas` - Listar tareas
- `POST /api/v1/tareas` - Crear tarea
- `PATCH /api/v1/tareas/{id}/estado` - Cambiar estado
- `PATCH /api/v1/tareas/{id}/asignar` - Asignar empleado
- `GET /api/v1/tareas/hoy` - Tareas de hoy
- `GET /api/v1/tareas/semana` - Tareas de la semana
- Y más...

### Personal (7 endpoints) ✨ Fase 2

- `GET /api/v1/personal` - Listar empleados
- `POST /api/v1/personal` - Crear empleado
- `GET /api/v1/personal/{id}/horas` - Horas trabajadas
- `GET /api/v1/personal/{id}/proyectos` - Proyectos asignados
- Y más...

### Horas (10 endpoints) ✨ Fase 2

- `GET /api/v1/horas` - Listar registros
- `POST /api/v1/horas` - Registrar horas
- `GET /api/v1/horas/empleado/{id}` - Por empleado
- `GET /api/v1/horas/proyecto/{id}` - Por proyecto
- `POST /api/v1/horas/calcular-mano-obra` - Calcular costo MO
- Y más...

### Notificaciones (10 endpoints) ✨ Fase 2

- `GET /api/v1/notificaciones` - Listar notificaciones
- `POST /api/v1/notificaciones` - Crear notificación
- `GET /api/v1/notificaciones/no-leidas` - No leídas
- `PATCH /api/v1/notificaciones/{id}/marcar-leida` - Marcar leída
- Y más...

**Total: ~74 endpoints activos**

Ver documentación completa en: http://localhost:8000/api/v1/docs

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/test_proyectos.py -v
```

## 🔐 Autenticación

La API usa JWT (JSON Web Tokens) para autenticación.

1. Registrar/Login para obtener token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

2. Usar el token en peticiones:

```bash
curl -X GET http://localhost:8000/api/v1/proyectos \
  -H "Authorization: Bearer <tu-token-aqui>"
```

## 👥 Roles de Usuario

- **admin**: Acceso completo al sistema
- **gerente**: Gestión de proyectos y validación de gastos
- **supervisor**: Validación de gastos y registro de horas
- **trabajador**: Reportar gastos y consultar tareas

## 📦 Storage de Archivos

El sistema soporta dos tipos de storage:

### Local (Desarrollo)
```env
STORAGE_TYPE=local
UPLOAD_DIR=./uploads
```

### MinIO (Producción)
```env
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=obras-facturas
```

## 🌱 Datos de Prueba

Para poblar la base de datos con datos de ejemplo (incluye datos de Fase 1 y Fase 2):

```bash
python scripts/seed_data.py
```

Esto creará:
- **4 usuarios** (admin, gerente, supervisor, trabajador)
- **4 proyectos** de ejemplo
- **8 gastos** en proyectos activos
- **5 empleados** con diferentes roles
- **6 tareas** asignadas a proyectos
- **23 registros de horas** de trabajo
- **5 notificaciones** de ejemplo

### Credenciales de prueba:

| Usuario | Username | Password | Rol |
|---------|----------|----------|-----|
| Admin | `admin` | `admin123` | ADMIN |
| Gerente | `jmartinez` | `gerente123` | GERENTE |
| Supervisor | `mgarcia` | `supervisor123` | SUPERVISOR |
| Trabajador | `plopez` | `trabajador123` | TRABAJADOR |

## 🤖 Bot de Telegram

El sistema incluye un bot de Telegram completamente funcional.

### Configurar el Bot

1. **Crear bot con BotFather:**
   - Habla con [@BotFather](https://t.me/BotFather) en Telegram
   - Envía `/newbot` y sigue las instrucciones
   - Guarda el token que te proporciona

2. **Configurar token en `.env`:**
   ```env
   TELEGRAM_BOT_TOKEN=tu-token-aqui
   ```

3. **Iniciar el bot:**
   ```bash
   cd bot
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

   O usar el script de inicio:
   ```bash
   ../scripts/start-bot.sh
   ```

### Comandos del Bot

- `/start` - Iniciar el bot y registrarse
- `/help` - Ver lista de comandos
- `/proyectos` - Ver proyectos activos
- `/tareas` - Ver tareas pendientes
- `/tareas_hoy` - Tareas de hoy
- `/mis_horas` - Resumen de horas trabajadas
- `/notificaciones` - Notificaciones pendientes
- `/estado` - Estado del sistema

## 🔄 Migrando de SQLite a PostgreSQL

Cuando estés listo para producción:

1. Actualiza `.env`:
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/obras
```

2. Ejecuta migraciones:
```bash
alembic upgrade head
```

## 🐛 Troubleshooting

### Error: "SECRET_KEY not set"
Asegúrate de tener un `.env` con SECRET_KEY definido.

### Error: "Database locked" (SQLite)
SQLite tiene limitaciones de concurrencia. Usa PostgreSQL para producción.

### Error al subir archivos
Verifica que el directorio `uploads/` exista y tenga permisos de escritura.

## 📝 Desarrollo

### Agregar un nuevo módulo

1. Crear estructura:
```
app/modules/mi_modulo/
├── __init__.py
├── models.py      # Modelos SQLAlchemy
├── schemas.py     # Schemas Pydantic
├── repository.py  # Acceso a datos
├── services.py    # Lógica de negocio
└── routes.py      # Endpoints FastAPI
```

2. Registrar router en `main.py`:
```python
from app.modules.mi_modulo.routes import router as mi_router
app.include_router(mi_router, prefix=settings.API_V1_PREFIX, tags=["MiModulo"])
```

### Código de calidad

```bash
# Formatear código
black app/

# Linting
flake8 app/

# Ordenar imports
isort app/
```

## 🚀 Deployment

Ver `docs/deployment.md` para instrucciones de deployment en producción.

## 📄 Licencia

Privado - Sistema de Gestión de Obras Mark-I
