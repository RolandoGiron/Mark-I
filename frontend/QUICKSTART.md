# Quick Start - Mark-I Frontend

Guía rápida para levantar el frontend en menos de 5 minutos.

## Prerrequisitos

- Node.js 18+ instalado
- Backend de Mark-I corriendo en `http://localhost:8000`

## Pasos Rápidos

### 1. Instalar Dependencias

```bash
cd /home/rolando/Desarrollo/Mark-I/frontend
npm install
```

### 2. Verificar Variables de Entorno

El archivo `.env` ya está configurado con:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_TIMEZONE=America/Guatemala
VITE_LOCALE=es-GT
```

### 3. Iniciar Desarrollo

```bash
npm run dev
```

La app estará en: **http://localhost:3000**

### 4. Login

Usa las credenciales del backend:

```
Usuario: admin
Contraseña: admin123
```

## Verificación

### Type Check (debe pasar sin errores)

```bash
npm run type-check
```

**Resultado esperado**: Sin errores ✅

### Build (verificar que compile)

```bash
npm run build
```

## Estructura de Navegación

Una vez logueado, tendrás acceso a:

- **Dashboard** (`/dashboard`) - ✅ Implementado
  - KPIs principales
  - Gráficas
  - Proyectos en alerta
  - Notificaciones

- **Proyectos** (`/proyectos`) - 🔲 Placeholder
- **Costos** (`/costos`) - 🔲 Placeholder
- **Tareas** (`/tareas`) - 🔲 Placeholder
- **Personal** (`/personal`) - 🔲 Placeholder
- **Horas** (`/horas`) - 🔲 Placeholder
- **Notificaciones** (`/notificaciones`) - 🔲 Placeholder

## Características Disponibles

### Autenticación ✅
- Login con validación
- Sesión persistente
- Redirect automático
- Logout

### Dashboard ✅
- Proyectos activos
- Gastos totales
- Tareas pendientes
- Notificaciones sin leer
- Gráfica de proyectos por estado
- Top 5 categorías de gasto
- Alertas de proyectos
- Notificaciones recientes

### UI/UX ✅
- Tema oscuro/claro
- Sidebar responsive
- Loading states (Skeletons)
- Toast notifications
- Navegación completa

## Troubleshooting

### Error: Cannot connect to API

**Problema**: El backend no está corriendo

**Solución**:
```bash
cd /home/rolando/Desarrollo/Mark-I/backend
source venv/bin/activate
uvicorn src.api.main:app --reload
```

### Error: CORS

**Problema**: Backend no acepta requests del frontend

**Solución**: Verificar en `backend/src/core/config.py`:
```python
BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
```

### Error: 401 Unauthorized

**Problema**: Token expirado o inválido

**Solución**: Hacer logout y login nuevamente

### Página en blanco

**Problema**: Error de JavaScript en el navegador

**Solución**:
1. Abrir DevTools (F12)
2. Ver errores en Console
3. Verificar que el backend esté respondiendo

## Desarrollo

### Hot Reload

Vite tiene Hot Module Replacement (HMR) automático. Los cambios se reflejan instantáneamente.

### Agregar una Nueva Página

1. Crear componente en `src/features/[modulo]/components/`
2. Agregar ruta en `src/routes/index.tsx`
3. Agregar link en `src/layouts/MainLayout.tsx`

Ejemplo:

```tsx
// 1. src/features/proyectos/components/ProyectosPage.tsx
export function ProyectosPage() {
  return <div>Lista de Proyectos</div>
}

// 2. src/routes/index.tsx
import { ProyectosPage } from '@/features/proyectos/components/ProyectosPage'

// Agregar en children:
{
  path: 'proyectos',
  element: <ProyectosPage />,
}

// 3. MainLayout.tsx ya tiene el link configurado
```

### Usar APIs

Todas las APIs están listas en `src/shared/api/`:

```tsx
import { useQuery } from '@tanstack/react-query'
import { proyectosApi } from '@/shared/api'

function MiComponente() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['proyectos'],
    queryFn: () => proyectosApi.getAll(),
  })

  if (isLoading) return <Skeleton />
  if (error) return <div>Error</div>

  return <div>{data?.items.map(...)}</div>
}
```

### Crear un Formulario

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'

const schema = z.object({
  nombre: z.string().min(3),
  email: z.string().email(),
})

type FormData = z.infer<typeof schema>

function MiFormulario() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Input {...register('nombre')} />
      {errors.nombre && <span>{errors.nombre.message}</span>}

      <Input {...register('email')} />
      {errors.email && <span>{errors.email.message}</span>}

      <Button type="submit">Enviar</Button>
    </form>
  )
}
```

### Mostrar Toast Notification

```tsx
import { useToast } from '@/shared/components/ui/use-toast'

function MiComponente() {
  const { toast } = useToast()

  const handleClick = () => {
    toast({
      title: 'Éxito',
      description: 'Operación completada',
      variant: 'success',
    })
  }

  return <Button onClick={handleClick}>Mostrar Toast</Button>
}
```

## Recursos

- **Documentación completa**: Ver `README.md`
- **Estado de implementación**: Ver `IMPLEMENTATION_STATUS.md`
- **Tipos TypeScript**: `src/shared/types/index.ts`
- **Componentes UI**: `src/shared/components/ui/`

## Soporte

Para problemas o preguntas, revisar:
1. Console del navegador (F12)
2. Network tab para ver requests
3. Backend logs
4. Este documento

---

**Última actualización**: 2025-11-14
