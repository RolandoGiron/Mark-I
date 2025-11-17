# Docker Setup - Mark-I

## 📋 Contenedores Disponibles

### Infraestructura
- **db** (PostgreSQL 15): Base de datos principal
- **redis**: Cache y message broker
- **minio**: Almacenamiento S3-compatible para archivos

### Aplicación
- **backend** (FastAPI): API REST
- **frontend** (React + Vite): Interfaz de usuario

## 🚀 Inicio Rápido

### 1. Desarrollo (Todos los servicios)

```bash
# Iniciar todos los contenedores en modo desarrollo
docker-compose up -d

# Ver logs
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f frontend
docker-compose logs -f backend
```

### 2. Solo Backend + Infraestructura

```bash
docker-compose up -d db redis minio backend
```

### 3. Solo Frontend (requiere backend corriendo localmente)

```bash
# Asegúrate de que el backend esté corriendo en localhost:8000
docker-compose up -d frontend
```

## 🔧 Configuración

### Frontend - Modos de Ejecución

#### Modo Desarrollo (por defecto)
```yaml
# En docker-compose.yml
target: development  # Usa Vite dev server
ports:
  - "3000:3000"
```

#### Modo Producción
```yaml
# En docker-compose.yml
target: production  # Usa Nginx + build optimizado
ports:
  - "80:80"
```

Para cambiar de modo:
1. Edita `docker-compose.yml`
2. Cambia `target: development` por `target: production`
3. Comenta el puerto 3000 y descomenta el puerto 80
4. Reconstruye: `docker-compose up -d --build frontend`

### Variables de Entorno

#### Backend
Configuradas en `docker-compose.yml`:
- `DATABASE_URL`: Conexión a PostgreSQL
- `REDIS_URL`: Conexión a Redis
- `MINIO_*`: Configuración de MinIO

#### Frontend
Configuradas en `docker-compose.yml`:
- `VITE_API_BASE_URL`: URL del backend
- `VITE_TIMEZONE`: America/Guatemala
- `VITE_LANGUAGE`: es-GT

## 📦 Comandos Útiles

### Reconstruir Contenedores

```bash
# Reconstruir todos
docker-compose up -d --build

# Reconstruir solo frontend
docker-compose up -d --build frontend

# Reconstruir solo backend
docker-compose up -d --build backend
```

### Detener y Limpiar

```bash
# Detener todos los contenedores
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Borra la BD)
docker-compose down -v

# Limpiar imágenes no usadas
docker system prune -a
```

### Ejecutar Comandos dentro de Contenedores

```bash
# Shell en el backend
docker-compose exec backend bash

# Shell en el frontend
docker-compose exec frontend sh

# Ejecutar tests del backend
docker-compose exec backend pytest

# Ejecutar migrations
docker-compose exec backend alembic upgrade head

# Seed data
docker-compose exec backend python scripts/seed_data.py

# Instalar dependencias del frontend
docker-compose exec frontend npm install
```

### Logs y Debugging

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de los últimos 100 líneas
docker-compose logs --tail=100

# Ver logs de un servicio
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f db

# Verificar estado de contenedores
docker-compose ps

# Ver uso de recursos
docker stats
```

## 🌐 URLs de Acceso

Cuando todos los servicios estén corriendo:

- **Frontend**: http://localhost:3000 (desarrollo) o http://localhost (producción)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **MinIO Console**: http://localhost:9001 (usuario: minioadmin, password: minioadmin)
- **PostgreSQL**: localhost:5432 (usuario: obras_user, password: obras_pass)
- **Redis**: localhost:6379

## 🔍 Health Checks

Todos los contenedores tienen health checks configurados:

```bash
# Ver estado de salud
docker-compose ps

# Inspeccionar health check de un contenedor
docker inspect mark-i-frontend
docker inspect mark-i-backend
docker inspect mark-i-db
```

## 📁 Volúmenes

Los datos persisten en volúmenes Docker:

- `mark-i-postgres-data`: Datos de PostgreSQL
- `mark-i-redis-data`: Datos de Redis
- `mark-i-minio-data`: Archivos de MinIO

### Backup de Datos

```bash
# Backup de PostgreSQL
docker-compose exec db pg_dump -U obras_user obras > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U obras_user obras < backup.sql

# Listar volúmenes
docker volume ls | grep mark-i

# Inspeccionar un volumen
docker volume inspect mark-i-postgres-data
```

## 🛠️ Troubleshooting

### Frontend no se conecta al backend

1. Verifica que el backend esté corriendo: `docker-compose ps backend`
2. Verifica la variable `VITE_API_BASE_URL` en `docker-compose.yml`
3. Revisa los logs: `docker-compose logs -f backend`

### Error de permisos en volúmenes

```bash
# Linux: ajustar permisos
sudo chown -R $USER:$USER ./frontend ./backend
```

### Hot reload no funciona

Para desarrollo local, es mejor correr el frontend fuera de Docker:
```bash
cd frontend
npm install
npm run dev
```

Y solo usar Docker para la infraestructura:
```bash
docker-compose up -d db redis minio backend
```

### Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs frontend

# Reconstruir forzadamente
docker-compose up -d --build --force-recreate frontend

# Verificar Dockerfile
docker build -f docker/Dockerfile.frontend --target development ./frontend
```

### Base de datos no se conecta

```bash
# Verificar que PostgreSQL esté listo
docker-compose exec db pg_isready -U obras_user

# Reiniciar contenedor de DB
docker-compose restart db

# Ver logs de la BD
docker-compose logs -f db
```

## 🚀 Deployment en Producción

### 1. Configurar Variables de Entorno

Crea un archivo `.env.production`:

```env
# Backend
DATABASE_URL=postgresql://user:pass@db:5432/obras
SECRET_KEY=tu-secret-key-segura
MINIO_ENDPOINT=minio:9000

# Frontend
VITE_API_BASE_URL=https://api.tu-dominio.com/api/v1
```

### 2. Actualizar docker-compose.yml

```yaml
frontend:
  target: production  # Build optimizado
  ports:
    - "80:80"
  environment:
    VITE_API_BASE_URL: ${VITE_API_BASE_URL}
```

### 3. Build y Deploy

```bash
# Build para producción
docker-compose -f docker-compose.yml build

# Iniciar en producción
docker-compose up -d

# Verificar
docker-compose ps
```

### 4. Nginx Reverse Proxy (Opcional)

Si quieres servir todo desde un solo dominio (ej: `app.tu-dominio.com`):

- Frontend: `app.tu-dominio.com`
- Backend: `app.tu-dominio.com/api`

El archivo `nginx.conf` ya está configurado para proxy al backend.

## 📝 Notas

- En **desarrollo**, se recomienda correr el frontend fuera de Docker para mejor hot reload
- En **producción**, usa `target: production` para builds optimizados con Nginx
- Los volúmenes persisten datos incluso si los contenedores se eliminan
- Los health checks aseguran que los servicios dependientes estén listos antes de iniciar

## 🔐 Seguridad

**IMPORTANTE**: En producción:
- [ ] Cambiar credenciales de PostgreSQL
- [ ] Cambiar credenciales de MinIO
- [ ] Generar un SECRET_KEY seguro para JWT
- [ ] Usar HTTPS (agregar certificados SSL)
- [ ] Configurar CORS apropiadamente
- [ ] Deshabilitar hot reload del backend
- [ ] Usar builds optimizados (target: production)

---

**Versión**: 1.0.0
**Última Actualización**: 2025-11-15
