# Mark-I Backend - API Endpoints Quick Reference

**Total Endpoints:** ~74 activos (Fase 1 + Fase 2 completadas)

## System Endpoints
```
GET  /                    # Root info
GET  /health              # Health check
```

## Authentication (`/api/v1/auth`) - 9 endpoints
```
POST   /auth/register                    # Register user
POST   /auth/login                       # Login & get JWT
GET    /auth/me                          # Get current user (JWT required)
PUT    /auth/me                          # Update own profile (JWT required)
POST   /auth/me/change-password          # Change password (JWT required)
GET    /auth/usuarios                    # List users (ADMIN only)
GET    /auth/usuarios/{usuario_id}       # Get user by ID (ADMIN only)
PUT    /auth/usuarios/{usuario_id}       # Update user (ADMIN only)
DELETE /auth/usuarios/{usuario_id}       # Delete user (ADMIN only)
```

## Projects (`/api/v1/proyectos`) - 8 endpoints
```
GET    /proyectos                        # List projects (paginated)
POST   /proyectos                        # Create project
GET    /proyectos/{id}                   # Get project by ID
GET    /proyectos/codigo/{codigo}        # Get project by code
PUT    /proyectos/{id}                   # Update project
DELETE /proyectos/{id}                   # Delete project
GET    /proyectos/{id}/resumen           # Financial summary
GET    /proyectos/stats/general          # Project statistics
```

## Expenses (`/api/v1/costos`) - 9 endpoints
```
GET    /costos                           # List expenses (paginated)
POST   /costos                           # Create expense
GET    /costos/{id}                      # Get expense by ID
PUT    /costos/{id}                      # Update expense
DELETE /costos/{id}                      # Delete expense
POST   /costos/{id}/factura              # Upload invoice file
POST   /costos/{id}/validar              # Validate/reject expense
GET    /costos/proyecto/{id}/total       # Project spending total
GET    /costos/stats/general             # Expense statistics
```

## Tasks (`/api/v1/tareas`) - 11 endpoints ✨ NEW
```
GET    /tareas                           # List tasks (paginated)
POST   /tareas                           # Create task
GET    /tareas/{id}                      # Get task by ID
PUT    /tareas/{id}                      # Update task
DELETE /tareas/{id}                      # Delete task
PATCH  /tareas/{id}/estado               # Change task status
PATCH  /tareas/{id}/asignar              # Assign employee to task
GET    /tareas/proyecto/{proyecto_id}    # Tasks by project
GET    /tareas/empleado/{empleado_id}    # Tasks by employee
GET    /tareas/hoy                       # Today's tasks
GET    /tareas/semana                    # This week's tasks
```

## Personnel (`/api/v1/personal`) - 7 endpoints ✨ NEW
```
GET    /personal                         # List employees (paginated)
POST   /personal                         # Create employee
GET    /personal/{id}                    # Get employee by ID
PUT    /personal/{id}                    # Update employee
DELETE /personal/{id}                    # Delete employee
GET    /personal/{id}/horas              # Employee hours worked
GET    /personal/{id}/proyectos          # Assigned projects
```

## Hours (`/api/v1/horas`) - 10 endpoints ✨ NEW
```
GET    /horas                                      # List hour records (paginated)
POST   /horas                                      # Register hours
GET    /horas/{id}                                 # Get hour record by ID
PUT    /horas/{id}                                 # Update hour record
DELETE /horas/{id}                                 # Delete hour record
GET    /horas/empleado/{empleado_id}               # Summary by employee
GET    /horas/proyecto/{proyecto_id}               # Summary by project
GET    /horas/empleado/{emp_id}/proyecto/{proy_id} # Specific summary
GET    /horas/stats/general                        # General statistics
POST   /horas/calcular-mano-obra                   # Calculate labor cost
```

## Notifications (`/api/v1/notificaciones`) - 10 endpoints ✨ NEW
```
GET    /notificaciones                             # List notifications (paginated)
POST   /notificaciones                             # Create notification
GET    /notificaciones/{id}                        # Get notification by ID
PUT    /notificaciones/{id}                        # Update notification
DELETE /notificaciones/{id}                        # Delete notification
PATCH  /notificaciones/{id}/marcar-leida           # Mark as read
GET    /notificaciones/no-leidas                   # Unread notifications
GET    /notificaciones/usuario/{usuario_id}        # Notifications by user
GET    /notificaciones/proyecto/{proyecto_id}      # Notifications by project
POST   /notificaciones/marcar-todas-leidas         # Mark all as read
```

---

## Common Request Examples

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

### Create Project
```bash
curl -X POST http://localhost:8000/api/v1/proyectos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "CASA-001",
    "nombre": "Casa Nueva",
    "cliente": "Juan Pérez",
    "presupuesto_total": 50000
  }'
```

### List Projects with Filters
```bash
curl -X GET 'http://localhost:8000/api/v1/proyectos?estado=en_progreso&page=1&page_size=10' \
  -H "Authorization: Bearer <token>"
```

### Create Expense
```bash
curl -X POST http://localhost:8000/api/v1/costos \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "proyecto_id": "project-uuid",
    "categoria": "materiales",
    "monto": 1500.00,
    "descripcion": "Cemento y arena",
    "proveedor_nombre": "Ferretería ABC"
  }'
```

### Upload Invoice
```bash
curl -X POST http://localhost:8000/api/v1/costos/{costo_id}/factura \
  -H "Authorization: Bearer <token>" \
  -F "file=@factura.pdf"
```

### Create Task ✨ NEW
```bash
curl -X POST http://localhost:8000/api/v1/tareas \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "proyecto_id": "project-uuid",
    "titulo": "Instalar ventanas",
    "descripcion": "Instalar ventanas en sala principal",
    "prioridad": "alta",
    "fecha_programada": "2025-11-10",
    "asignado_a": "empleado-uuid"
  }'
```

### Create Employee ✨ NEW
```bash
curl -X POST http://localhost:8000/api/v1/personal \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "telefono": "+1234567890",
    "especialidad": "Electricista",
    "costo_hora": 25.00,
    "activo": true
  }'
```

### Register Hours ✨ NEW
```bash
curl -X POST http://localhost:8000/api/v1/horas \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "empleado_id": "empleado-uuid",
    "proyecto_id": "proyecto-uuid",
    "horas": 8,
    "fecha": "2025-11-09",
    "descripcion": "Instalación eléctrica"
  }'
```

### Create Notification ✨ NEW
```bash
curl -X POST http://localhost:8000/api/v1/notificaciones \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": "usuario-uuid",
    "tipo": "advertencia",
    "titulo": "Presupuesto excedido",
    "mensaje": "El proyecto ha excedido el 90% del presupuesto",
    "proyecto_id": "proyecto-uuid"
  }'
```

---

## Query Parameters

### Pagination (all list endpoints)
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 50, max: 100)

### Projects Filter
- `estado` - Filter by state (prospecto, cotizacion, aprobado, en_progreso, pausado, completado, cancelado)
- `cliente` - Filter by client name (partial match)
- `search` - Search across code, name, client, description

### Expenses Filter
- `proyecto_id` - Filter by project ID
- `categoria` - Filter by category (materiales, mano_obra, transporte, herramientas, subcontrato, permisos, servicios, otros)
- `fecha_desde` - Start date (YYYY-MM-DD format)
- `fecha_hasta` - End date (YYYY-MM-DD format)
- `validado` - true/false - Filter by validation status
- `con_factura` - true/false - Filter by invoice presence
- `search` - Search in description and provider
- `periodo` - Statistics period (hoy, semana, mes, año, todos)

### Tasks Filter ✨ NEW
- `proyecto_id` - Filter by project ID
- `empleado_id` - Filter by assigned employee
- `estado` - Filter by status (pendiente, en_progreso, completada, cancelada)
- `prioridad` - Filter by priority (alta, media, baja)
- `fecha_desde` - Start date (YYYY-MM-DD format)
- `fecha_hasta` - End date (YYYY-MM-DD format)
- `search` - Search in title and description

### Personnel Filter ✨ NEW
- `activo` - true/false - Filter by active status
- `especialidad` - Filter by specialty
- `search` - Search in name and phone

### Hours Filter ✨ NEW
- `empleado_id` - Filter by employee ID
- `proyecto_id` - Filter by project ID
- `fecha_desde` - Start date (YYYY-MM-DD format)
- `fecha_hasta` - End date (YYYY-MM-DD format)

### Notifications Filter ✨ NEW
- `usuario_id` - Filter by user ID
- `proyecto_id` - Filter by project ID
- `tipo` - Filter by type (info, advertencia, error, exito)
- `leida` - true/false - Filter by read status
- `fecha_desde` - Start date (YYYY-MM-DD format)
- `fecha_hasta` - End date (YYYY-MM-DD format)

---

## Response Status Codes
```
200 - OK (successful GET, PUT, DELETE)
201 - Created (successful POST)
400 - Bad Request (validation error)
401 - Unauthorized (missing/invalid token)
403 - Forbidden (insufficient permissions)
404 - Not Found (resource doesn't exist)
500 - Internal Server Error
```

---

## Authentication Header
```
Authorization: Bearer <your-jwt-token-here>
```

---

## User Roles & Permissions
```
ADMIN:
  - Everything (full access)
  
GERENTE:
  - Manage projects
  - Validate expenses
  - View statistics
  
SUPERVISOR:
  - Validate expenses
  - Track hours
  - View assigned projects
  
TRABAJADOR:
  - Report expenses
  - View assigned tasks
  - Limited project access
```

---

## Swagger UI & Documentation
```
Swagger UI: http://localhost:8000/api/v1/docs
ReDoc:     http://localhost:8000/api/v1/redoc
OpenAPI:   http://localhost:8000/api/v1/openapi.json
```
