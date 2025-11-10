# Guía de Tests - Mark-I Backend

Esta guía explica cómo ejecutar las pruebas automatizadas del backend usando pytest siguiendo TDD (Test-Driven Development).

## Estructura de Tests

```
backend/
├── conftest.py              # Fixtures globales y configuración
├── pytest.ini               # Configuración de pytest
└── tests/
    ├── __init__.py
    ├── test_system.py       # Tests de endpoints del sistema
    ├── test_auth.py         # Tests de autenticación
    ├── test_proyectos.py    # Tests de proyectos
    └── test_costos.py       # Tests de costos/gastos
```

## Cobertura de Tests

### Endpoints Cubiertos (30+ tests)

#### Sistema (test_system.py)
- ✅ `GET /health` - Health check
- ✅ `GET /` - Root endpoint
- ✅ `GET /api/v1/openapi.json` - Documentación OpenAPI

#### Autenticación (test_auth.py)
- ✅ `POST /api/v1/auth/register` - Registro de usuarios
- ✅ `POST /api/v1/auth/login` - Inicio de sesión
- ✅ `GET /api/v1/auth/me` - Obtener usuario actual
- ✅ `PUT /api/v1/auth/me` - Actualizar perfil
- ✅ `POST /api/v1/auth/me/change-password` - Cambiar contraseña
- ✅ `GET /api/v1/auth/usuarios` - Listar usuarios (admin)
- ✅ `GET /api/v1/auth/usuarios/{id}` - Obtener usuario (admin)
- ✅ `PUT /api/v1/auth/usuarios/{id}` - Actualizar usuario (admin)
- ✅ `DELETE /api/v1/auth/usuarios/{id}` - Eliminar usuario (admin)

#### Proyectos (test_proyectos.py)
- ✅ `GET /api/v1/proyectos` - Listar proyectos
- ✅ `POST /api/v1/proyectos` - Crear proyecto
- ✅ `GET /api/v1/proyectos/{id}` - Obtener proyecto por ID
- ✅ `GET /api/v1/proyectos/codigo/{codigo}` - Obtener proyecto por código
- ✅ `PUT /api/v1/proyectos/{id}` - Actualizar proyecto
- ✅ `DELETE /api/v1/proyectos/{id}` - Eliminar proyecto
- ✅ `GET /api/v1/proyectos/{id}/resumen` - Resumen financiero
- ✅ `GET /api/v1/proyectos/stats/general` - Estadísticas

#### Costos (test_costos.py)
- ✅ `GET /api/v1/costos` - Listar costos
- ✅ `POST /api/v1/costos` - Crear costo
- ✅ `GET /api/v1/costos/{id}` - Obtener costo por ID
- ✅ `PUT /api/v1/costos/{id}` - Actualizar costo
- ✅ `DELETE /api/v1/costos/{id}` - Eliminar costo
- ✅ `POST /api/v1/costos/{id}/factura` - Subir factura
- ✅ `POST /api/v1/costos/{id}/validar` - Validar/rechazar costo
- ✅ `GET /api/v1/costos/proyecto/{id}/total` - Total por proyecto
- ✅ `GET /api/v1/costos/stats/general` - Estadísticas

## Instalación de Dependencias

Las dependencias de testing están incluidas en `requirements-dev.txt` (para desarrollo sin PostgreSQL):

```bash
cd backend

# Opción recomendada para desarrollo/testing (usa SQLite, no requiere PostgreSQL)
pip install -r requirements-dev.txt

# O si prefieres instalar TODO (requiere PostgreSQL instalado)
pip install -r requirements-prod.txt
```

**Nota:** Para testing solo necesitas `requirements-dev.txt` que usa SQLite. Si obtienes errores con `psycopg2-binary`, usa este archivo.

Dependencias clave:
- `pytest==7.4.3` - Framework de testing
- `pytest-asyncio==0.21.1` - Soporte para tests async
- `pytest-cov==4.1.0` - Reportes de cobertura
- `httpx==0.25.2` - Cliente HTTP para tests

## Comandos para Ejecutar Tests

### 1. Ejecutar TODOS los tests

```bash
pytest
```

o con más detalles:

```bash
pytest -v
```

### 2. Ejecutar tests de un módulo específico

```bash
# Solo tests de autenticación
pytest tests/test_auth.py -v

# Solo tests de proyectos
pytest tests/test_proyectos.py -v

# Solo tests de costos
pytest tests/test_costos.py -v

# Solo tests del sistema
pytest tests/test_system.py -v
```

### 3. Ejecutar tests con marcadores (tags)

```bash
# Solo tests de autenticación
pytest -m auth -v

# Solo tests de proyectos
pytest -m proyectos -v

# Solo tests de costos
pytest -m costos -v

# Solo tests de admin
pytest -m admin -v

# Solo tests de integración
pytest -m integration -v

# Solo tests unitarios
pytest -m unit -v
```

### 4. Ejecutar un test específico

```bash
# Por nombre de clase
pytest tests/test_auth.py::TestAuthLogin -v

# Por nombre de función
pytest tests/test_auth.py::TestAuthLogin::test_login_success_with_username -v
```

### 5. Ver cobertura de código

```bash
# Ejecutar con reporte de cobertura
pytest --cov=app --cov-report=html

# Ver reporte en el navegador
# El reporte HTML se genera en: htmlcov/index.html
```

### 6. Ejecutar tests en paralelo (más rápido)

```bash
# Instalar pytest-xdist primero
pip install pytest-xdist

# Ejecutar en paralelo
pytest -n auto
```

### 7. Ejecutar tests con mayor detalle de errores

```bash
# Ver traceback completo
pytest --tb=long

# Ver solo la primera falla y parar
pytest -x

# Ver stdout incluso en tests exitosos
pytest -s
```

## Fixtures Disponibles

### Configuración
- `test_settings` - Settings de testing
- `db_engine` - Engine de base de datos de test
- `db_session` - Sesión de BD para cada test
- `client` - Cliente HTTP de FastAPI

### Usuarios
- `admin_user` - Usuario con rol ADMIN
- `gerente_user` - Usuario con rol GERENTE
- `supervisor_user` - Usuario con rol SUPERVISOR
- `trabajador_user` - Usuario con rol TRABAJADOR
- `inactive_user` - Usuario inactivo

### Tokens
- `admin_token` - Token JWT de admin
- `gerente_token` - Token JWT de gerente
- `supervisor_token` - Token JWT de supervisor
- `trabajador_token` - Token JWT de trabajador

### Helpers
- `auth_headers(token)` - Helper para crear headers de autenticación
- `create_user_payload(username, email, rol)` - Helper para crear payload de usuario
- `password_plain` - Contraseña de prueba ("Test123456")

## Estructura de un Test

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.unit  # Marcador opcional
class TestMiModulo:
    """Descripción de los tests"""

    def test_algo_exitoso(self, client: TestClient, admin_token, auth_headers):
        """Test de caso exitoso"""
        response = client.get(
            "/api/v1/endpoint",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["campo"] == "valor esperado"

    def test_algo_falla(self, client: TestClient):
        """Test de caso de error"""
        response = client.get("/api/v1/endpoint")

        assert response.status_code == 401
```

## Buenas Prácticas

### 1. Naming Convention
- Archivos: `test_*.py`
- Clases: `Test*`
- Funciones: `test_*`
- Fixtures: nombres descriptivos sin `test_`

### 2. Organización
- Agrupar tests relacionados en clases
- Un test por comportamiento/escenario
- Tests independientes (no dependen de orden)

### 3. Assertions
- Usar assertions claras y específicas
- Verificar códigos de estado HTTP
- Validar estructura de respuestas
- Comprobar efectos secundarios

### 4. Marcadores
```python
@pytest.mark.unit         # Tests unitarios
@pytest.mark.integration  # Tests de integración
@pytest.mark.slow         # Tests lentos
@pytest.mark.auth         # Tests de autenticación
@pytest.mark.admin        # Requiere permisos admin
```

## Continuous Integration (CI/CD)

### GitHub Actions (ejemplo)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-fail-under=80
```

## Solución de Problemas

### Error: "No module named 'app'"

```bash
# Asegúrate de estar en el directorio backend
cd backend
pytest
```

### Error: "Database locked"

```bash
# Los tests usan SQLite en memoria, si hay problemas:
# 1. Elimina archivos .db antiguos
rm -f test.db *.db

# 2. Ejecuta los tests
pytest
```

### Tests lentos

```bash
# Ejecuta solo tests rápidos (excluye los marcados como slow)
pytest -m "not slow"
```

### Ver qué fixtures están disponibles

```bash
pytest --fixtures
```

## Métricas Objetivo

- **Cobertura de código**: ≥ 80% (configurado en pytest.ini)
- **Tests pasando**: 100%
- **Tiempo de ejecución**: < 30 segundos para suite completa

## Siguientes Pasos

1. ✅ Ejecutar todos los tests: `pytest -v`
2. ✅ Verificar cobertura: `pytest --cov=app --cov-report=html`
3. ✅ Revisar reporte HTML en `htmlcov/index.html`
4. 🔄 Agregar más tests según sea necesario
5. 🔄 Configurar CI/CD
6. 🔄 Implementar tests de performance

## Recursos Adicionales

- [Documentación de pytest](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

## Contacto

Para preguntas o problemas con los tests, consulta la documentación del proyecto o abre un issue.
