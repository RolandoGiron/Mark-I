# Mark-I Frontend

Sistema de gestión de proyectos de construcción - Interfaz de usuario.

## Stack Tecnológico

- **React 18.3** - Framework UI
- **TypeScript 5.6** - Tipado estático
- **Vite 5.4** - Build tool
- **React Router 6.28** - Enrutamiento
- **TanStack Query 5** - Gestión de estado del servidor
- **Zustand 5** - Gestión de estado global
- **React Hook Form 7** - Formularios
- **Zod 3** - Validación de esquemas
- **Tailwind CSS 3.4** - Estilos
- **Radix UI** - Componentes accesibles
- **Lucide React** - Iconos
- **Recharts 2** - Gráficas
- **Axios 1.7** - Cliente HTTP

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── features/              # Módulos por funcionalidad
│   │   ├── auth/
│   │   │   └── components/
│   │   │       └── LoginPage.tsx
│   │   └── dashboard/
│   │       └── components/
│   │           └── DashboardPage.tsx
│   ├── layouts/               # Layouts principales
│   │   └── MainLayout.tsx
│   ├── routes/                # Configuración de rutas
│   │   └── index.tsx
│   └── shared/                # Código compartido
│       ├── api/               # Clientes API
│       │   ├── client.ts
│       │   ├── auth.ts
│       │   ├── proyectos.ts
│       │   ├── costos.ts
│       │   ├── tareas.ts
│       │   ├── personal.ts
│       │   ├── horas.ts
│       │   └── notificaciones.ts
│       ├── components/
│       │   └── ui/            # Componentes UI reutilizables
│       │       ├── button.tsx
│       │       ├── input.tsx
│       │       ├── card.tsx
│       │       ├── label.tsx
│       │       ├── select.tsx
│       │       ├── dialog.tsx
│       │       ├── toast.tsx
│       │       ├── badge.tsx
│       │       ├── table.tsx
│       │       └── skeleton.tsx
│       ├── hooks/             # Custom hooks (a implementar)
│       ├── lib/               # Utilidades y configuraciones
│       │   ├── utils.ts
│       │   └── react-query.ts
│       ├── store/             # Zustand stores
│       │   ├── auth.ts
│       │   └── theme.ts
│       └── types/             # Tipos TypeScript
│           └── index.ts
├── .env.example               # Variables de entorno ejemplo
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Instalación

### Requisitos Previos

- Node.js 18+ y npm
- Backend de Mark-I corriendo en `http://localhost:8000`

### Pasos

1. **Clonar el repositorio** (si aún no lo has hecho):
   ```bash
   cd /home/rolando/Desarrollo/Mark-I/frontend
   ```

2. **Instalar dependencias**:
   ```bash
   npm install
   ```

3. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   ```

   Editar `.env` si es necesario:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   VITE_TIMEZONE=America/Guatemala
   VITE_LOCALE=es-GT
   ```

4. **Iniciar servidor de desarrollo**:
   ```bash
   npm run dev
   ```

   La aplicación estará disponible en `http://localhost:5173`

## Scripts Disponibles

```bash
# Desarrollo
npm run dev              # Inicia servidor de desarrollo

# Build
npm run build            # Genera build de producción
npm run preview          # Preview del build de producción

# Linting y Type Checking
npm run lint             # Ejecuta ESLint
npm run type-check       # Verifica tipos TypeScript
```

## Características Implementadas

### Componentes UI (Basados en Shadcn/ui)

- ✅ Button - Botones con variantes
- ✅ Input - Campos de entrada
- ✅ Card - Tarjetas de contenido
- ✅ Label - Etiquetas de formulario
- ✅ Select - Dropdown select
- ✅ Dialog - Modales
- ✅ Toast - Notificaciones toast
- ✅ Badge - Badges de estado
- ✅ Table - Tablas
- ✅ Skeleton - Loading placeholders

### Páginas

- ✅ **Login** (`/login`) - Autenticación de usuarios
- ✅ **Dashboard** (`/dashboard`) - Vista general con KPIs y gráficas
- 🔲 **Proyectos** (`/proyectos`) - Lista y gestión de proyectos
- 🔲 **Detalle de Proyecto** (`/proyectos/:id`) - Información detallada
- 🔲 **Costos** (`/costos`) - Gestión de gastos
- 🔲 **Tareas** (`/tareas`) - Gestión de tareas
- 🔲 **Personal** (`/personal`) - Gestión de empleados
- 🔲 **Horas** (`/horas`) - Registro de horas trabajadas
- 🔲 **Notificaciones** (`/notificaciones`) - Centro de notificaciones

### Funcionalidades Core

- ✅ **Autenticación** - Login con JWT
- ✅ **Rutas Protegidas** - Middleware de autenticación
- ✅ **Tema Oscuro/Claro** - Toggle de tema persistente
- ✅ **React Query** - Caché y sincronización con API
- ✅ **Navegación Responsive** - Sidebar adaptable
- ✅ **Toast Notifications** - Sistema de notificaciones
- ✅ **Loading States** - Skeletons durante carga
- ✅ **Error Handling** - Manejo de errores en API

### API Integration

Todos los módulos del backend están integrados:

- ✅ Auth API - Autenticación y usuarios
- ✅ Proyectos API - CRUD de proyectos
- ✅ Costos API - Gestión de gastos
- ✅ Tareas API - Gestión de tareas
- ✅ Personal API - Gestión de empleados
- ✅ Horas API - Registro de horas
- ✅ Notificaciones API - Centro de notificaciones

## Dashboard

El dashboard incluye:

- **KPIs Principales**:
  - Proyectos activos
  - Gastos totales
  - Tareas pendientes
  - Notificaciones sin leer

- **Gráficas**:
  - Proyectos por estado (Pie chart)
  - Top 5 categorías de gasto (Bar chart)

- **Alertas**:
  - Proyectos en alerta (sobrepresupuesto o cerca del límite)
  - Notificaciones recientes

## Soporte UTF-8 y Regionalización

Toda la aplicación está configurada para:

- ✅ **Encoding UTF-8** completo
- ✅ **Zona horaria**: `America/Guatemala` (UTC-6)
- ✅ **Locale**: `es-GT` (Español Guatemala)
- ✅ **Validación de caracteres latinos**: á, é, í, ó, ú, ñ, ü
- ✅ **Formato de moneda**: Quetzales (Q)

## Próximos Pasos

1. **Implementar páginas restantes**:
   - Proyectos (lista, crear, editar, eliminar)
   - Costos (registro, validación, upload de facturas)
   - Tareas (kanban board, asignaciones)
   - Personal (CRUD de empleados)
   - Horas (registro diario, reportes)
   - Notificaciones (lista, marcar como leídas)

2. **Funcionalidades avanzadas**:
   - Filtros y búsqueda avanzada
   - Exportación a Excel/PDF
   - Gráficas interactivas adicionales
   - Drag & drop para tareas
   - Upload de archivos (facturas, fotos)
   - Websockets para notificaciones en tiempo real

3. **Optimizaciones**:
   - Code splitting
   - Lazy loading de componentes
   - Virtualización de listas largas
   - PWA (Progressive Web App)

## Credenciales de Prueba

Usa las credenciales configuradas en el backend:

```
Usuario: admin
Contraseña: admin123
```

## Troubleshooting

### Error de CORS

Si recibes errores de CORS, asegúrate que el backend tenga configurado:

```python
# backend/src/api/main.py
BACKEND_CORS_ORIGINS = ["http://localhost:5173"]
```

### Error de conexión API

Verifica que:
1. El backend esté corriendo en `http://localhost:8000`
2. La variable `VITE_API_BASE_URL` en `.env` sea correcta

### Errores de TypeScript

Ejecuta el type checker:
```bash
npm run type-check
```

## Tecnologías y Decisiones de Diseño

### ¿Por qué Vite?
- Build ultra rápido
- Hot Module Replacement (HMR) instantáneo
- Configuración simple

### ¿Por qué Zustand sobre Redux?
- API más simple
- Menos boilerplate
- Mejor performance

### ¿Por qué React Query?
- Gestión automática de caché
- Refetch inteligente
- Optimistic updates
- Menos código para manejo de estado del servidor

### ¿Por qué Radix UI?
- Accesibilidad (ARIA) out-of-the-box
- Unstyled (full control con Tailwind)
- Componentes robustos y probados

## Contribuir

1. Crear branch desde `mvp-candidate1`
2. Seguir convenciones de código (ver `CLAUDE.md` global)
3. Usar TypeScript estricto
4. Seguir patrón de componentes existente
5. Actualizar este README si es necesario

## Licencia

Proyecto privado - Mark-I © 2025

---

**Versión**: 0.1.0
**Última actualización**: 2025-11-14
**Mantenedor**: Rolando
