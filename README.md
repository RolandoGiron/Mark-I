# Mark-I - Sistema de Gestión de Obras y Costos

Sistema integral para gestión de proyectos de construcción con enfoque en control financiero y operativo.

## 📋 Descripción

Mark-I es una solución completa para empresas constructoras que necesitan:

- ✅ Control de costos en tiempo real por proyecto
- ✅ Captura de datos desde campo vía Telegram
- ✅ Dashboards intuitivos para toma de decisiones
- ✅ Gestión completa de tareas y asignaciones

## 🏗️ Arquitectura

- **Backend:** FastAPI + SQLAlchemy + PostgreSQL/SQLite
- **Storage:** Sistema de archivos local / MinIO (S3-compatible)
- **Autenticación:** JWT (JSON Web Tokens)
- **Bot:** Telegram Bot ✅
- **Frontend:** React + Vite (Próximamente)

## 🚀 Quick Start

### Desarrollo Rápido (SQLite)

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd Mark-I

# 2. Setup backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar entorno
cp .env.example .env
# Editar .env con tu configuración

# 4. Iniciar servidor
uvicorn app.main:app --reload
```

Abre http://localhost:8000/api/v1/docs para ver la documentación interactiva.

### Con Docker (Completo)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Acceder a:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/api/v1/docs
# - MinIO Console: http://localhost:9001
```

## 📁 Estructura del Proyecto

```
Mark-I/
├── backend/              # API FastAPI
│   ├── app/
│   │   ├── modules/     # Módulos de negocio
│   │   │   ├── auth/           # Autenticación ✅
│   │   │   ├── proyectos/      # Proyectos ✅
│   │   │   ├── costos/         # Gastos ✅
│   │   │   ├── tareas/         # Tareas ✅
│   │   │   ├── personal/       # Personal ✅
│   │   │   ├── horas/          # Registro de Horas ✅
│   │   │   └── notificaciones/ # Notificaciones ✅
│   │   ├── shared/      # Código compartido
│   │   └── utils/       # Utilidades
│   └── tests/          # Tests
├── bot/                 # Telegram Bot ✅
├── frontend/           # React App (Próximamente)
├── docker/            # Dockerfiles
├── scripts/           # Scripts de utilidad
└── claude.md        # Documentación del sistema
```

## 📚 Documentación

- **[claude.md](./claude.md)** - Documentación técnica completa del sistema
- **[PlanImplementacion.md](./PlanImplementacion.md)** - Plan detallado de implementación por fases
- **[backend/README.md](./backend/README.md)** - Documentación del backend API

## 🎯 Estado del Proyecto

### ✅ Fase 1 - Completada (13/13 tareas)

- [x] Setup del repositorio y estructura
- [x] Configuración de base de datos (SQLite/PostgreSQL)
- [x] API básica con FastAPI
- [x] Autenticación JWT
- [x] Módulo de Proyectos (CRUD completo)
- [x] Módulo de Costos (CRUD + upload de facturas)
- [x] Sistema de storage (Local + MinIO)
- [x] Docker Compose setup
- [x] Scripts de seed y desarrollo
- [x] Documentación completa

### ✅ Fase 2 - Completada (8/8 tareas)

- [x] Módulo de Tareas (11 endpoints - CRUD completo)
- [x] Módulo de Personal (7 endpoints - Gestión de empleados)
- [x] Módulo de Registro de Horas (10 endpoints - Control de tiempo)
- [x] Cálculo automático de costos de mano de obra
- [x] Sistema de notificaciones (10 endpoints - Alertas y avisos)
- [x] Bot de Telegram - Setup y estructura
- [x] Bot de Telegram - Comandos básicos (8 comandos)
- [x] Bot de Telegram - Consulta de tareas y proyectos

**Total Fase 2:** ~48 endpoints adicionales, ~60 archivos, ~8000 líneas de código

### ⏳ Fase 3 - Pendiente

- [ ] Integración OCR (Tesseract/EasyOCR)
- [ ] Speech-to-Text (Whisper)
- [ ] Procesamiento inteligente de facturas
- [ ] Migraciones Alembic para nuevos modelos
- [ ] Tests completos (80%+ coverage)

## 🔧 Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validación de datos
- **JWT** - Autenticación segura
- **Alembic** - Migraciones de base de datos

### Storage
- **Local Filesystem** - Para desarrollo
- **MinIO** - S3-compatible para producción

### Base de Datos
- **SQLite** - Desarrollo
- **PostgreSQL** - Producción

## 📊 Features Implementados

### Gestión de Proyectos
- CRUD completo de proyectos
- Seguimiento de presupuesto
- Estados de proyecto (prospecto, en progreso, completado, etc.)
- Cálculo de días transcurridos y restantes
- Resumen financiero por proyecto

### Gestión de Costos
- Registro de gastos con categorías
- Upload de facturas (JPG, PNG, PDF)
- Validación de gastos
- Filtros avanzados (fecha, proyecto, categoría)
- Estadísticas y totales
- Alertas de presupuesto excedido

### Gestión de Tareas
- CRUD completo de tareas
- Asignación de tareas a empleados
- Estados y prioridades
- Tareas por proyecto
- Filtros por estado, prioridad y fecha
- Tareas del día y de la semana

### Gestión de Personal
- CRUD de empleados
- Roles y especialidades
- Costos por hora configurables
- Asignación a proyectos
- Seguimiento de disponibilidad

### Registro de Horas
- Registro de horas trabajadas por empleado
- Resúmenes por proyecto y empleado
- Cálculo automático de costos de mano de obra
- Estadísticas de productividad
- Filtros por fecha y proyecto

### Sistema de Notificaciones
- Creación y gestión de notificaciones
- Notificaciones por usuario y proyecto
- Tipos: info, advertencia, error, éxito
- Sistema de alertas automáticas
- Marcado de leído/no leído

### Bot de Telegram
- Comandos básicos (/start, /help, /proyectos, /tareas)
- Consulta de proyectos y tareas
- Registro de gastos (pendiente integración completa)
- Notificaciones automáticas
- Interfaz conversacional amigable

### Autenticación
- Registro e inicio de sesión
- JWT tokens
- Roles de usuario (admin, gerente, supervisor, trabajador)
- Permisos por rol
- Cambio de contraseña

## 🔐 Seguridad

- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración
- Validación de permisos por rol
- CORS configurado
- Validación de datos con Pydantic

## 🧪 Testing

```bash
cd backend
pytest
pytest --cov=app --cov-report=html
```

## 📖 API Endpoints

### Autenticación (9 endpoints)
- `POST /api/v1/auth/register` - Registro
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Usuario actual
- `PUT /api/v1/auth/me` - Actualizar perfil
- `POST /api/v1/auth/me/change-password` - Cambiar contraseña
- `GET /api/v1/auth/usuarios` - Listar usuarios (Admin)
- `GET /api/v1/auth/usuarios/{id}` - Obtener usuario (Admin)
- `PUT /api/v1/auth/usuarios/{id}` - Actualizar usuario (Admin)
- `DELETE /api/v1/auth/usuarios/{id}` - Eliminar usuario (Admin)

### Proyectos (8 endpoints)
- `GET /api/v1/proyectos` - Listar
- `POST /api/v1/proyectos` - Crear
- `GET /api/v1/proyectos/{id}` - Obtener
- `GET /api/v1/proyectos/codigo/{codigo}` - Obtener por código
- `PUT /api/v1/proyectos/{id}` - Actualizar
- `DELETE /api/v1/proyectos/{id}` - Eliminar
- `GET /api/v1/proyectos/{id}/resumen` - Resumen financiero
- `GET /api/v1/proyectos/stats/general` - Estadísticas

### Costos (9 endpoints)
- `GET /api/v1/costos` - Listar
- `POST /api/v1/costos` - Crear
- `GET /api/v1/costos/{id}` - Obtener
- `PUT /api/v1/costos/{id}` - Actualizar
- `DELETE /api/v1/costos/{id}` - Eliminar
- `POST /api/v1/costos/{id}/factura` - Subir factura
- `POST /api/v1/costos/{id}/validar` - Validar
- `GET /api/v1/costos/proyecto/{id}/total` - Total por proyecto
- `GET /api/v1/costos/stats/general` - Estadísticas

### Tareas (11 endpoints)
- `GET /api/v1/tareas` - Listar tareas
- `POST /api/v1/tareas` - Crear tarea
- `GET /api/v1/tareas/{id}` - Obtener tarea
- `PUT /api/v1/tareas/{id}` - Actualizar tarea
- `DELETE /api/v1/tareas/{id}` - Eliminar tarea
- `PATCH /api/v1/tareas/{id}/estado` - Cambiar estado
- `PATCH /api/v1/tareas/{id}/asignar` - Asignar empleado
- `GET /api/v1/tareas/proyecto/{id}` - Tareas por proyecto
- `GET /api/v1/tareas/empleado/{id}` - Tareas por empleado
- `GET /api/v1/tareas/hoy` - Tareas de hoy
- `GET /api/v1/tareas/semana` - Tareas de la semana

### Personal (7 endpoints)
- `GET /api/v1/personal` - Listar empleados
- `POST /api/v1/personal` - Crear empleado
- `GET /api/v1/personal/{id}` - Obtener empleado
- `PUT /api/v1/personal/{id}` - Actualizar empleado
- `DELETE /api/v1/personal/{id}` - Eliminar empleado
- `GET /api/v1/personal/{id}/horas` - Horas trabajadas
- `GET /api/v1/personal/{id}/proyectos` - Proyectos asignados

### Horas (10 endpoints)
- `GET /api/v1/horas` - Listar registros
- `POST /api/v1/horas` - Registrar horas
- `GET /api/v1/horas/{id}` - Obtener registro
- `PUT /api/v1/horas/{id}` - Actualizar registro
- `DELETE /api/v1/horas/{id}` - Eliminar registro
- `GET /api/v1/horas/empleado/{id}` - Resumen por empleado
- `GET /api/v1/horas/proyecto/{id}` - Resumen por proyecto
- `GET /api/v1/horas/empleado/{emp_id}/proyecto/{proy_id}` - Resumen específico
- `GET /api/v1/horas/stats/general` - Estadísticas generales
- `POST /api/v1/horas/calcular-mano-obra` - Calcular costo de mano de obra

### Notificaciones (10 endpoints)
- `GET /api/v1/notificaciones` - Listar notificaciones
- `POST /api/v1/notificaciones` - Crear notificación
- `GET /api/v1/notificaciones/{id}` - Obtener notificación
- `PUT /api/v1/notificaciones/{id}` - Actualizar notificación
- `DELETE /api/v1/notificaciones/{id}` - Eliminar notificación
- `PATCH /api/v1/notificaciones/{id}/marcar-leida` - Marcar como leída
- `GET /api/v1/notificaciones/no-leidas` - Notificaciones no leídas
- `GET /api/v1/notificaciones/usuario/{id}` - Por usuario
- `GET /api/v1/notificaciones/proyecto/{id}` - Por proyecto
- `POST /api/v1/notificaciones/marcar-todas-leidas` - Marcar todas como leídas

**Total: ~74 endpoints activos**

Ver documentación completa en: http://localhost:8000/api/v1/docs

## 🚀 Próximos Pasos

1. **Migraciones:** Crear migraciones Alembic para los nuevos modelos de Fase 2
2. **Tests:** Implementar tests para los módulos de Fase 2 (coverage 80%+)
3. **Frontend:** Desarrollo de dashboard web con React
4. **Fase 3:** Integración de OCR y Speech-to-Text
5. **Bot Telegram:** Configurar token y activar comandos avanzados
6. **Fase 4:** Optimización y deployment en producción

## 🤝 Contribución

Este es un proyecto privado. Para contribuir, contacta al administrador.

## 📝 Licencia

Privado - Sistema de Gestión de Obras Mark-I © 2025

## 📞 Contacto

Para soporte o consultas, contacta al equipo de desarrollo.
