# CLAUDE.md - Mark-I: Sistema de Gestión de Obras

> **📍 Ubicación**: `/home/rolando/Desarrollo/Mark-I/CLAUDE.md`
> **🎯 Propósito**: Documentación del estado actual, decisiones arquitectónicas y próximos pasos del proyecto Mark-I

---

## 📊 Estado del Proyecto

- **Fase Actual**: Fase 3 - Frontend MVP (En Progreso)
- **Última Actualización**: 2025-11-14
- **Progreso General**: ~75% (Backend completo + Frontend base)

### Configuración Regional
- **Zona Horaria**: UTC-6 (America/Guatemala)
- **Locale**: es_GT (Español Guatemala / Centro América)
- **Encoding**: UTF-8 (soporte completo de acentos y ñ)
- **Moneda**: GTQ (Quetzales)

---

## ✅ Fases Completadas

### Fase 1: Backend Core (✅ COMPLETADA - 13/13 tareas)
- [x] Configuración base del proyecto (FastAPI + SQLAlchemy + Alembic)
- [x] Sistema de autenticación con JWT
- [x] CRUD completo de Proyectos
- [x] CRUD completo de Costos con upload de facturas
- [x] CRUD completo de Tareas
- [x] CRUD completo de Personal/Empleados
- [x] Sistema de Registro de Horas
- [x] Sistema de Notificaciones
- [x] Validación de gastos (gerente/supervisor)
- [x] Cálculo automático de mano de obra
- [x] Estadísticas y resúmenes por módulo
- [x] Storage de archivos (local/MinIO)
- [x] Tests unitarios básicos

### Fase 2: Backend Avanzado (✅ COMPLETADA - 8/8 tareas)
- [x] Filtros avanzados en todos los endpoints
- [x] Paginación consistente
- [x] Sistema de permisos por rol (admin, gerente, supervisor, trabajador)
- [x] Validaciones Pydantic completas con soporte UTF-8
- [x] Manejo de errores global
- [x] Documentación OpenAPI/Swagger
- [x] Variables de entorno configuradas
- [x] Script de seed data para desarrollo

### Fase 3: Frontend Base (🔄 EN PROGRESO - 9/15 tareas)
- [x] Estructura del proyecto (Vite + React + TypeScript)
- [x] Configuración de Tailwind CSS + Shadcn/ui
- [x] Setup de React Query + Zustand
- [x] Cliente API completo (8 servicios)
- [x] Tipos TypeScript completos
- [x] Sistema de autenticación (login, logout, perfil)
- [x] Layout principal con sidebar responsive
- [x] Dashboard con KPIs y gráficos
- [x] Sistema de tema oscuro/claro
- [ ] CRUD de Proyectos
- [ ] CRUD de Costos con upload de facturas
- [ ] Sistema de Tareas (Kanban)
- [ ] CRUD de Personal
- [ ] Registro de Horas
- [ ] Centro de Notificaciones

---

## 🏛️ Decisiones Arquitectónicas

### Backend

**Arquitectura elegida**: Arquitectura por Capas (Simple)

**Justificación**:
- Sistema de gestión CRUD con lógica de negocio moderada
- Equipo pequeño/individual
- Necesidad de velocidad de desarrollo
- Complejidad suficiente para MVP sin sobre-ingeniería

**Stack Tecnológico**:
- **Framework**: FastAPI 0.115+
- **Base de Datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **ORM**: SQLAlchemy 2.0+ con modelos declarativos
- **Migraciones**: Alembic
- **Validación**: Pydantic v2 con soporte UTF-8
- **Autenticación**: JWT con python-jose
- **Storage**: Sistema de archivos local / MinIO (S3-compatible)
- **Testing**: Pytest + pytest-asyncio + pytest-cov

**Estructura del Backend**:
```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Lógica de negocio
│   ├── api/v1/routes/   # Endpoints HTTP
│   ├── core/            # Config, security, database
│   └── storage/         # Manejo de archivos
├── scripts/             # Scripts de utilidad
├── tests/               # Tests
└── migrations/          # Alembic
```

**Trade-offs aceptados**:
- Menor separación entre capas vs DDD/Clean (más rápido de desarrollar)
- Acoplamiento moderado al framework (FastAPI) pero mayor productividad
- Lógica de negocio en servicios (no en dominio puro) pero suficiente para el alcance

---

### Frontend

**Arquitectura elegida**: Feature-based con Shared Components

**Justificación**:
- Escalabilidad por módulos independientes
- Reutilización de componentes
- Separación clara de responsabilidades
- Fácil mantenimiento y testing

**Stack Tecnológico**:
- **Framework**: React 18.3+ con TypeScript
- **Build Tool**: Vite 5.4+
- **Styling**: Tailwind CSS 3.4+
- **Componentes UI**: Shadcn/ui (Radix UI + Tailwind)
- **State Management**:
  - React Query (TanStack Query) para server state
  - Zustand para client state (auth, theme)
- **Routing**: React Router v6
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts 2.15+
- **Export**: xlsx (Excel) + jsPDF (PDF)
- **Icons**: Lucide React

**Estructura del Frontend**:
```
frontend/
├── src/
│   ├── features/           # Módulos por funcionalidad
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── proyectos/
│   │   ├── costos/
│   │   ├── tareas/
│   │   ├── personal/
│   │   ├── horas/
│   │   └── notificaciones/
│   ├── shared/
│   │   ├── components/ui/  # Componentes Shadcn/ui
│   │   ├── api/            # Clientes HTTP
│   │   ├── store/          # Zustand stores
│   │   ├── lib/            # Utilidades
│   │   └── types/          # TypeScript types
│   ├── layouts/            # Layouts principales
│   └── routes/             # Configuración de rutas
```

**Trade-offs aceptados**:
- Más archivos y estructura vs simplicidad (mejor organización a largo plazo)
- Dependencia de Radix UI (más componentes complejos pero accesibles)
- Bundle size mayor (muchas libs) pero mejor DX y UX

---

## 🔑 Características Principales Implementadas

### Backend (74 endpoints activos)

#### 1. Autenticación y Usuarios (`/api/v1/auth`)
- ✅ Login con JWT
- ✅ Registro de usuarios
- ✅ Gestión de perfil
- ✅ Cambio de contraseña
- ✅ CRUD de usuarios (admin only)
- ✅ Sistema de roles: admin, gerente, supervisor, trabajador

#### 2. Proyectos (`/api/v1/proyectos`)
- ✅ CRUD completo
- ✅ Estados: prospecto, cotización, aprobado, en_progreso, pausado, completado, cancelado
- ✅ Resumen financiero (presupuesto vs gastado)
- ✅ Alertas de sobrepresupuesto (>90%)
- ✅ Estadísticas generales
- ✅ Filtros avanzados

#### 3. Costos/Gastos (`/api/v1/costos`)
- ✅ CRUD completo
- ✅ Categorías: materiales, mano_obra, transporte, herramientas, subcontrato, permisos, servicios, otros
- ✅ Upload de facturas (JPG, PNG, PDF)
- ✅ Sistema de validación (gerente/supervisor)
- ✅ Cálculo automático de mano de obra por periodo
- ✅ Estadísticas por categoría y periodo
- ✅ Filtros: proyecto, categoría, fechas, validación, factura

#### 4. Tareas (`/api/v1/tareas`)
- ✅ CRUD completo
- ✅ Estados: pendiente, en_progreso, completada, cancelada
- ✅ Prioridades: baja, media, alta, urgente
- ✅ Asignación a empleados
- ✅ Fechas de vencimiento
- ✅ Tareas vencidas y del día
- ✅ Estadísticas completas

#### 5. Personal/Empleados (`/api/v1/personal`)
- ✅ CRUD completo (admin only)
- ✅ Tarifa por hora
- ✅ Estado activo/inactivo
- ✅ Vinculación con usuarios
- ✅ Estadísticas por cargo

#### 6. Registro de Horas (`/api/v1/horas`)
- ✅ CRUD completo
- ✅ Registro diario de horas trabajadas
- ✅ Vinculación con proyecto y tarea
- ✅ Cálculo de horas extras (>8h)
- ✅ Resúmenes por empleado y proyecto
- ✅ Estadísticas de productividad

#### 7. Notificaciones (`/api/v1/notificaciones`)
- ✅ CRUD completo
- ✅ Tipos: alerta_presupuesto, tarea_asignada, tarea_vencida, gasto_pendiente, etc.
- ✅ Sistema de lectura (marcar como leída)
- ✅ Notificaciones recientes (24h)
- ✅ Estadísticas

### Frontend (Parcialmente implementado)

#### Componentes Implementados (36 archivos)
- ✅ 12 componentes UI reutilizables (Button, Input, Card, Dialog, Select, etc.)
- ✅ Layout principal con sidebar responsive
- ✅ Sistema de autenticación completo
- ✅ Dashboard con KPIs y gráficos
- ✅ Sistema de toasts para notificaciones
- ✅ Toggle de tema oscuro/claro
- ✅ 8 clientes API completos
- ✅ TypeScript strict mode con tipos completos

#### Páginas Completadas
1. ✅ **LoginPage** - Autenticación con validación
2. ✅ **DashboardPage** - KPIs, gráficos, alertas, notificaciones

#### Páginas Pendientes (Placeholders creados)
3. ⏳ **ProyectosPage** - Lista y CRUD
4. ⏳ **ProyectoDetallePage** - Vista detallada con tabs
5. ⏳ **CostosPage** - CRUD y validación
6. ⏳ **TareasPage** - Tablero Kanban
7. ⏳ **PersonalPage** - CRUD empleados
8. ⏳ **HorasPage** - Registro diario
9. ⏳ **NotificacionesPage** - Centro completo

---

## 🚀 Próximos Pasos

### Fase 3 - Completar Frontend CRUD (Prioridad Alta)

1. **Módulo de Proyectos** (Estimado: 3-4 horas)
   - [ ] Lista de proyectos con tabla y filtros
   - [ ] Modal crear/editar proyecto
   - [ ] Vista detallada con tabs (info, costos, tareas, horas)
   - [ ] Gráfico de presupuesto vs gastado
   - [ ] Cambio de estado de proyecto

2. **Módulo de Costos** (Estimado: 3-4 horas)
   - [ ] Lista de costos con filtros avanzados
   - [ ] Modal crear/editar costo
   - [ ] Upload de factura con preview
   - [ ] Sistema de validación (aprobar/rechazar)
   - [ ] Modal de cálculo de mano de obra
   - [ ] Gráficos por categoría

3. **Módulo de Tareas** (Estimado: 4-5 horas)
   - [ ] Tablero Kanban drag & drop
   - [ ] Modal crear/editar tarea
   - [ ] Asignación de empleados
   - [ ] Filtros por proyecto, empleado, prioridad
   - [ ] Vista de calendario
   - [ ] Alertas de tareas vencidas

4. **Módulo de Personal** (Estimado: 2-3 horas)
   - [ ] Lista de empleados con filtros
   - [ ] Modal crear/editar empleado
   - [ ] Tarjeta de empleado con estadísticas
   - [ ] Historial de horas trabajadas

5. **Módulo de Horas** (Estimado: 2-3 horas)
   - [ ] Formulario de registro diario
   - [ ] Tabla de registros con filtros
   - [ ] Resumen por empleado/proyecto
   - [ ] Gráfico de horas trabajadas

6. **Módulo de Notificaciones** (Estimado: 2 horas)
   - [ ] Centro de notificaciones
   - [ ] Filtros por tipo
   - [ ] Marcar como leída/todas leídas
   - [ ] Badge con contador en header

### Fase 4 - Reportes y Exportación (Prioridad Media)

7. **Sistema de Reportes** (Estimado: 3-4 horas)
   - [ ] Exportar proyectos a Excel/PDF
   - [ ] Exportar costos a Excel/PDF
   - [ ] Reporte de horas trabajadas
   - [ ] Reporte financiero consolidado
   - [ ] Gráficos avanzados (tendencias, comparativas)

### Fase 5 - Testing y Optimización (Prioridad Media)

8. **Testing Frontend** (Estimado: 4-5 horas)
   - [ ] Tests unitarios con Vitest
   - [ ] Tests de integración de React Query
   - [ ] Tests E2E con Playwright (flujos críticos)
   - [ ] Cobertura mínima 70%

9. **Optimizaciones** (Estimado: 2-3 horas)
   - [ ] Code splitting avanzado
   - [ ] Lazy loading de rutas
   - [ ] Optimización de imágenes
   - [ ] PWA (opcional)

### Fase 6 - Deployment (Prioridad Baja)

10. **Preparación para Producción** (Estimado: 3-4 horas)
    - [ ] Variables de entorno de producción
    - [ ] Build optimizado
    - [ ] Docker containers (backend + frontend)
    - [ ] Nginx como reverse proxy
    - [ ] CI/CD con GitHub Actions
    - [ ] Backups automáticos de BD

---

## 📋 Notas Técnicas Importantes

### Backend

1. **Base de Datos**:
   - Desarrollo: SQLite (`obras.db`)
   - Producción: PostgreSQL recomendado
   - Encoding: UTF-8 obligatorio
   - Timezone: Almacenar en UTC, convertir a UTC-6 para display

2. **Autenticación**:
   - JWT con expiración de 30 minutos (configurable)
   - Refresh automático NO implementado (futuro)
   - Tokens en header: `Authorization: Bearer <token>`

3. **Storage**:
   - Desarrollo: `./uploads/` (filesystem local)
   - Producción: MinIO (S3-compatible) recomendado
   - Facturas: max 10MB, formatos: JPG, PNG, PDF

4. **Validaciones**:
   - Todos los campos de texto soportan UTF-8 y caracteres latinos
   - Regex para nombres: `^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$`
   - Validación de email estándar

### Frontend

1. **Environment Variables**:
   - `VITE_API_BASE_URL`: URL del backend (default: http://localhost:8000/api/v1)
   - `VITE_API_TIMEOUT`: Timeout de requests (default: 30000ms)
   - `VITE_TIMEZONE`: America/Guatemala
   - `VITE_LANGUAGE`: es-GT

2. **React Query**:
   - Stale time: 5 minutos
   - Cache time: 10 minutos
   - Retry: 1 vez
   - RefetchOnWindowFocus: true

3. **Persistencia**:
   - Auth state: localStorage + Zustand persist
   - Theme: localStorage + Zustand persist
   - Server state: React Query cache (memoria)

4. **Responsividad**:
   - Mobile: < 768px
   - Tablet: 768px - 1024px
   - Desktop: > 1024px
   - Sidebar colapsable en mobile

---

## 🐛 Issues Conocidos

1. **Backend**:
   - ⚠️ Refresh token no implementado (logout manual cada 30 min)
   - ⚠️ Notificaciones en tiempo real solo con polling (no WebSockets)
   - ⚠️ Tests de integración incompletos

2. **Frontend**:
   - ⚠️ Páginas CRUD pendientes (solo placeholders)
   - ⚠️ Drag & drop de Kanban por implementar
   - ⚠️ Tests E2E pendientes
   - ⚠️ Optimización de bundle size pendiente

---

## 📚 Recursos y Documentación

### Backend
- **API Docs**: http://localhost:8000/api/v1/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Código**: `/backend/`
- **Tests**: `pytest tests/ -v --cov=app`

### Frontend
- **Dev Server**: http://localhost:3000
- **Build**: `npm run build`
- **Preview**: `npm run preview`
- **Type Check**: `npm run type-check`
- **Código**: `/frontend/`

### Scripts Útiles
```bash
# Backend
cd backend
python scripts/seed_data.py        # Crear datos de prueba
python -m pytest                   # Ejecutar tests
python -m alembic upgrade head     # Migrar BD

# Frontend
cd frontend
npm install                        # Instalar dependencias
npm run dev                        # Iniciar desarrollo
npm run build                      # Build producción
```

---

## 👥 Roles y Permisos

| Acción                      | Admin | Gerente | Supervisor | Trabajador |
|-----------------------------|-------|---------|------------|------------|
| Crear/Editar Proyectos      | ✅    | ✅      | ❌         | ❌         |
| Ver Proyectos               | ✅    | ✅      | ✅         | ✅         |
| Crear Costos                | ✅    | ✅      | ✅         | ✅         |
| Validar Costos              | ✅    | ✅      | ✅         | ❌         |
| Crear/Editar Tareas         | ✅    | ✅      | ✅         | ❌         |
| Ver Tareas Asignadas        | ✅    | ✅      | ✅         | ✅         |
| Crear/Editar Empleados      | ✅    | ❌      | ❌         | ❌         |
| Registrar Horas             | ✅    | ✅      | ✅         | ✅         |
| Ver Estadísticas Generales  | ✅    | ✅      | ❌         | ❌         |
| Gestionar Usuarios          | ✅    | ❌      | ❌         | ❌         |

---

## 🔄 Historial de Cambios

### 2025-11-14 - Fase 3 Inicio
- ✅ Frontend base creado (estructura, config, tipos)
- ✅ 36 archivos TypeScript generados
- ✅ Login y Dashboard completamente funcionales
- ✅ Sistema de autenticación integrado
- ✅ Tema oscuro/claro implementado

### 2025-11-XX - Fase 2 Completada
- ✅ Backend completamente funcional
- ✅ 74 endpoints activos
- ✅ Sistema de permisos por rol
- ✅ Validaciones Pydantic completas
- ✅ Storage de archivos implementado

### 2025-11-XX - Fase 1 Completada
- ✅ Arquitectura base del backend
- ✅ CRUD de todos los módulos
- ✅ Sistema de autenticación JWT
- ✅ Migraciones con Alembic

---

**Mantenedor**: Rolando
**Versión**: 3.0.0
**Última Actualización**: 2025-11-14

> Este archivo debe actualizarse después de cada sesión de desarrollo significativa.
