# Guía de Instalación - Mark-I Backend

Esta guía te ayudará a instalar y configurar el backend del proyecto Mark-I.

## Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Git

## Instalación

### Opción 1: Desarrollo y Testing (Recomendado para comenzar)

Esta opción usa SQLite y **no requiere** PostgreSQL instalado.

```bash
# 1. Navegar al directorio del backend
cd backend

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar el entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# 3. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# 4. Copiar archivo de configuración
cp .env.example .env

# 5. Editar .env si es necesario (opcional para desarrollo)
# nano .env

# 6. Ejecutar tests para verificar instalación
pytest -v
```

### Opción 2: Producción (Con PostgreSQL)

Esta opción requiere PostgreSQL instalado en tu sistema.

#### Instalar PostgreSQL primero

**En Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev
```

**En Fedora/RHEL:**
```bash
sudo dnf install postgresql postgresql-server postgresql-devel
```

**En macOS (con Homebrew):**
```bash
brew install postgresql
```

**En Windows:**
Descarga el instalador desde: https://www.postgresql.org/download/windows/

#### Luego instalar dependencias de Python

```bash
# 1. Navegar al directorio del backend
cd backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate

# 3. Instalar dependencias de producción
pip install -r requirements-prod.txt

# 4. Configurar variables de entorno
cp .env.example .env
nano .env

# 5. Actualizar DATABASE_URL en .env
# DATABASE_URL=postgresql://usuario:password@localhost:5432/mark_i_db

# 6. Ejecutar migraciones
alembic upgrade head

# 7. (Opcional) Cargar datos de prueba
python scripts/seed_data.py
```

## Solución de Problemas

### Error: "pg_config executable not found"

Este error ocurre cuando intentas instalar `psycopg2-binary` sin tener PostgreSQL instalado.

**Soluciones:**

1. **Para desarrollo/testing:** Usa `requirements-dev.txt` en lugar de `requirements.txt`
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Para producción:** Instala PostgreSQL primero (ver sección arriba)

### Error: "No module named 'app'"

Asegúrate de estar en el directorio `backend`:
```bash
cd backend
pytest -v
```

### Error: "ModuleNotFoundError: No module named 'pytest'"

Las dependencias no están instaladas:
```bash
pip install -r requirements-dev.txt
```

### Error al ejecutar tests: "Database locked"

Elimina archivos de base de datos antiguos:
```bash
rm -f test.db *.db
pytest -v
```

## Verificar Instalación

### 1. Verificar que las dependencias están instaladas

```bash
pip list | grep fastapi
pip list | grep pytest
```

### 2. Ejecutar los tests

```bash
# Ejecutar todos los tests
pytest -v

# O usar el script
./run_tests.sh
```

Si todos los tests pasan (verde), ¡la instalación fue exitosa! ✅

### 3. Iniciar el servidor de desarrollo

```bash
# Opción 1: Usando uvicorn directamente
uvicorn app.main:app --reload

# Opción 2: Usando el script de Python
python -m app.main
```

Luego abre tu navegador en: http://localhost:8000

Documentación API: http://localhost:8000/api/v1/docs

## Estructura de Archivos de Dependencias

```
backend/
├── requirements.txt           # ORIGINAL - Todas las dependencias
├── requirements-dev.txt       # DESARROLLO - Sin PostgreSQL (SQLite)
├── requirements-prod.txt      # PRODUCCIÓN - Con PostgreSQL
└── requirements-test.txt      # Solo para CI/CD (próximamente)
```

## Cuándo Usar Cada Archivo

| Archivo | Cuándo Usarlo | Base de Datos |
|---------|---------------|---------------|
| `requirements-dev.txt` | Desarrollo local, testing | SQLite |
| `requirements-prod.txt` | Servidor de producción | PostgreSQL |
| `requirements.txt` | Legacy (usar los otros) | Ambas |

## Siguientes Pasos

Después de la instalación:

1. **Leer la documentación de tests:**
   ```bash
   cat README_TESTS.md
   ```

2. **Ejecutar los tests:**
   ```bash
   ./run_tests.sh
   ```

3. **Iniciar el servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Explorar la API:**
   - Documentación interactiva: http://localhost:8000/api/v1/docs
   - Health check: http://localhost:8000/health

## Desarrollo con Docker (Alternativa)

Si prefieres usar Docker (incluye PostgreSQL automáticamente):

```bash
# Desde el directorio raíz del proyecto
docker-compose up -d

# Los tests se ejecutan dentro del contenedor
docker-compose exec backend pytest -v
```

## Contacto y Soporte

Para problemas de instalación:
1. Revisa esta guía completa
2. Consulta los logs de error
3. Busca en Issues del proyecto
4. Crea un nuevo Issue con detalles del error

## Resumen Rápido

```bash
# Para desarrollo y testing (SIN PostgreSQL):
pip install -r requirements-dev.txt
pytest -v

# Para producción (CON PostgreSQL):
# 1. Instalar PostgreSQL en el sistema primero
# 2. Luego:
pip install -r requirements-prod.txt
```

¡Eso es todo! 🚀
