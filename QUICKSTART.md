# 🚀 Quick Start - Mark-I

Guía rápida para empezar a usar Mark-I en 5 minutos.

## Opción 1: Inicio Rápido Automático (Recomendado)

```bash
# Ejecutar script de inicio
./scripts/start-dev.sh
```

Este script automáticamente:
- ✅ Crea el entorno virtual
- ✅ Instala dependencias
- ✅ Configura variables de entorno
- ✅ Opcionalmente crea datos de prueba
- ✅ Inicia el servidor

## Opción 2: Inicio Manual

### 1. Preparar el entorno

```bash
# Crear y activar entorno virtual
cd backend
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y actualizar SECRET_KEY (importante!)
nano .env  # o tu editor preferido
```

### 3. Crear datos de prueba (opcional pero recomendado)

```bash
python scripts/seed_data.py
```

Esto crea:
- 4 usuarios (admin, gerente, supervisor, trabajador)
- 4 proyectos de ejemplo
- 8 gastos de ejemplo

### 4. Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

## 🌐 Acceder a la aplicación

Una vez iniciado el servidor:

- **API:** http://localhost:8000
- **Documentación Interactiva:** http://localhost:8000/api/v1/docs
- **Health Check:** http://localhost:8000/health

## 🔐 Credenciales de Prueba

Después de ejecutar el script de seed:

### Administrador
- **Username:** `admin`
- **Password:** `admin123`
- **Permisos:** Acceso total

### Gerente
- **Username:** `jmartinez`
- **Password:** `gerente123`
- **Permisos:** Gestión de proyectos y validación

### Supervisor
- **Username:** `mgarcia`
- **Password:** `supervisor123`
- **Permisos:** Validación de gastos

### Trabajador
- **Username:** `plopez`
- **Password:** `trabajador123`
- **Permisos:** Reportar gastos

## 📝 Primeros Pasos

### 1. Obtener un token de acceso

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Respuesta:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {...}
}
```

### 2. Usar el token en peticiones

```bash
# Guardar el token
TOKEN="tu-token-aqui"

# Listar proyectos
curl http://localhost:8000/api/v1/proyectos \
  -H "Authorization: Bearer $TOKEN"

# Crear un proyecto
curl -X POST http://localhost:8000/api/v1/proyectos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "CASA-005",
    "nombre": "Casa Nueva",
    "cliente": "Cliente Test",
    "presupuesto_total": 300000,
    "estado": "prospecto"
  }'
```

### 3. O usar la documentación interactiva

1. Abre http://localhost:8000/api/v1/docs
2. Click en "Authorize" (candado verde arriba a la derecha)
3. Ingresa el token: `Bearer tu-token-aqui`
4. ¡Listo! Ahora puedes probar todos los endpoints desde el navegador

## 🐳 Opción 3: Con Docker

Si prefieres usar Docker:

```bash
# Iniciar todos los servicios (PostgreSQL, Redis, MinIO, Backend)
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

El backend estará en http://localhost:8000

## ✅ Verificar que todo funciona

```bash
# Health check
curl http://localhost:8000/health

# Debería responder:
# {
#   "status": "healthy",
#   "app": "Mark-I - Sistema de Gestión de Obras",
#   "version": "1.0.0",
#   "environment": "development"
# }
```

## 📚 Próximos Pasos

1. **Explorar la API:** Revisa http://localhost:8000/api/v1/docs
2. **Leer la documentación:** Ve a `backend/README.md` para más detalles
3. **Ver el código:** Explora la estructura en `backend/app/modules/`
4. **Crear tu primer proyecto:** Usa la API o Swagger UI
5. **Subir una factura:** Prueba el endpoint de upload
6. **Crear tareas:** Prueba el módulo de tareas y asignaciones
7. **Registrar horas:** Usa el módulo de registro de horas
8. **Bot de Telegram:** Configura tu bot (ver sección Bot de Telegram)

## 🤖 Bot de Telegram

### Configuración del Bot

1. **Crear el bot en Telegram:**
   - Habla con [@BotFather](https://t.me/BotFather) en Telegram
   - Envía `/newbot` y sigue las instrucciones
   - Guarda el token que te proporciona

2. **Configurar el token:**
   ```bash
   # Edita backend/.env
   TELEGRAM_BOT_TOKEN=tu-token-aqui
   ```

3. **Iniciar el bot:**
   ```bash
   cd bot
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

### Comandos Disponibles

- `/start` - Iniciar el bot y registrarse
- `/help` - Ver lista de comandos disponibles
- `/proyectos` - Ver lista de proyectos activos
- `/tareas` - Ver tus tareas pendientes
- `/tareas_hoy` - Ver tareas de hoy
- `/mis_horas` - Ver resumen de horas trabajadas
- `/notificaciones` - Ver notificaciones pendientes
- `/estado` - Ver estado del sistema

### Uso del Bot

El bot permite interactuar con el sistema Mark-I desde Telegram:
- Consultar proyectos y tareas
- Ver notificaciones
- Registrar gastos (próximamente con OCR)
- Consultar estadísticas personales

## 🆘 Problemas Comunes

### Error: "ModuleNotFoundError"
```bash
# Asegúrate de estar en el entorno virtual
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### Error: "SECRET_KEY not set"
```bash
# Verifica que existe backend/.env
# y que tiene la variable SECRET_KEY definida
cat backend/.env | grep SECRET_KEY
```

### Puerto 8000 ocupado
```bash
# Cambiar el puerto en backend/.env
PORT=8001

# O especificarlo al iniciar
uvicorn app.main:app --reload --port 8001
```

### Base de datos bloqueada (SQLite)
```bash
# Eliminar la BD y recrearla
rm backend/obras.db
python backend/scripts/seed_data.py
```

## 💡 Tips

- **Hot Reload:** El servidor se recarga automáticamente al editar código
- **Logs:** Observa la terminal para ver requests y errores
- **Debug:** Activa `DEBUG=True` en `.env` para más detalles
- **PostgreSQL:** Para producción, cambia a PostgreSQL en `.env`

## 📖 Más Información

- **Documentación Completa:** [claude.md](./claude.md)
- **Plan de Implementación:** [PlanImplementacion.md](./PlanImplementacion.md)
- **Backend README:** [backend/README.md](./backend/README.md)

---

**¿Listo?** ¡Empieza a construir! 🏗️
