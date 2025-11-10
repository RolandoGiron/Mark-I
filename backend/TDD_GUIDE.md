# Guía de Test-Driven Development (TDD)

Esta guía explica cómo aplicar TDD (Test-Driven Development) en el proyecto Mark-I.

## ¿Qué es TDD?

TDD es una metodología de desarrollo donde:
1. **Escribes el test PRIMERO** (antes del código)
2. **El test falla** (porque no hay código)
3. **Escribes el código mínimo** para que el test pase
4. **Refactorizas** el código manteniendo los tests pasando

## Ciclo Red-Green-Refactor

```
🔴 RED    → Escribe un test que falla
   ↓
🟢 GREEN  → Escribe código mínimo para que pase
   ↓
🔵 REFACTOR → Mejora el código sin romper tests
   ↓
   └─────→ Repite
```

## Ejemplo Práctico: Agregar Endpoint de Notificaciones

### Paso 1: RED - Escribir el test primero

```python
# tests/test_notificaciones.py

import pytest
from fastapi.testclient import TestClient

@pytest.mark.notificaciones
class TestNotificaciones:
    """Tests para módulo de notificaciones"""

    def test_create_notificacion(self, client: TestClient, admin_token, auth_headers):
        """Test crear notificación"""
        data = {
            "titulo": "Nueva tarea",
            "mensaje": "Se asignó una nueva tarea",
            "tipo": "info",
            "usuario_id": "user-123"
        }

        response = client.post(
            "/api/v1/notificaciones",
            json=data,
            headers=auth_headers(admin_token)
        )

        # Esto FALLARÁ porque el endpoint no existe aún
        assert response.status_code == 201
        assert response.json()["titulo"] == "Nueva tarea"
        assert response.json()["leida"] == False
```

**Ejecutar el test:**
```bash
pytest tests/test_notificaciones.py -v
```

**Resultado esperado:** 🔴 FALLA (endpoint no existe)

### Paso 2: GREEN - Implementar código mínimo

```python
# app/modules/notificaciones/models.py

from sqlalchemy import Column, String, Boolean, Text
from app.database import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(String(36), primary_key=True)
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    tipo = Column(String(20), nullable=False)
    usuario_id = Column(String(36), nullable=False)
    leida = Column(Boolean, default=False)
```

```python
# app/modules/notificaciones/routes.py

from fastapi import APIRouter, status
from app.modules.notificaciones.models import Notificacion

router = APIRouter(prefix="/notificaciones")

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_notificacion(data: dict):
    # Implementación mínima
    return {
        "id": "123",
        "titulo": data["titulo"],
        "mensaje": data["mensaje"],
        "tipo": data["tipo"],
        "usuario_id": data["usuario_id"],
        "leida": False
    }
```

```python
# app/main.py

from app.modules.notificaciones.routes import router as notif_router

app.include_router(notif_router, prefix=settings.API_V1_PREFIX)
```

**Ejecutar el test:**
```bash
pytest tests/test_notificaciones.py -v
```

**Resultado esperado:** 🟢 PASA

### Paso 3: REFACTOR - Mejorar el código

Ahora que el test pasa, mejoramos el código:

```python
# app/modules/notificaciones/schemas.py

from pydantic import BaseModel, Field

class NotificacionCreate(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    mensaje: str = Field(..., min_length=1)
    tipo: str = Field(..., pattern="^(info|warning|error|success)$")
    usuario_id: str

class NotificacionResponse(NotificacionCreate):
    id: str
    leida: bool
    creado_en: datetime

    model_config = {"from_attributes": True}
```

```python
# app/modules/notificaciones/services.py

import uuid
from sqlalchemy.orm import Session
from app.modules.notificaciones.models import Notificacion
from app.modules.notificaciones.schemas import NotificacionCreate

class NotificacionService:
    def __init__(self, db: Session):
        self.db = db

    def create_notificacion(self, data: NotificacionCreate):
        notificacion = Notificacion(
            id=str(uuid.uuid4()),
            titulo=data.titulo,
            mensaje=data.mensaje,
            tipo=data.tipo,
            usuario_id=data.usuario_id,
            leida=False
        )
        self.db.add(notificacion)
        self.db.commit()
        self.db.refresh(notificacion)
        return notificacion
```

```python
# app/modules/notificaciones/routes.py (refactorizado)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.notificaciones.schemas import NotificacionCreate, NotificacionResponse
from app.modules.notificaciones.services import NotificacionService

router = APIRouter(prefix="/notificaciones")

def get_service(db: Session = Depends(get_db)):
    return NotificacionService(db)

@router.post("", response_model=NotificacionResponse, status_code=status.HTTP_201_CREATED)
async def create_notificacion(
    data: NotificacionCreate,
    service: NotificacionService = Depends(get_service)
):
    return service.create_notificacion(data)
```

**Ejecutar tests:**
```bash
pytest tests/test_notificaciones.py -v
```

**Resultado:** 🟢 Sigue pasando pero con mejor código

### Paso 4: Agregar más tests

Ahora agregamos tests para casos edge:

```python
# tests/test_notificaciones.py (continuación)

    def test_create_notificacion_invalid_tipo(self, client, admin_token, auth_headers):
        """Test crear notificación con tipo inválido"""
        data = {
            "titulo": "Test",
            "mensaje": "Mensaje",
            "tipo": "invalid_type",  # Tipo inválido
            "usuario_id": "user-123"
        }

        response = client.post(
            "/api/v1/notificaciones",
            json=data,
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 422

    def test_list_notificaciones_usuario(self, client, admin_token, auth_headers):
        """Test listar notificaciones de un usuario"""
        # Primero crear una notificación
        create_data = {
            "titulo": "Test",
            "mensaje": "Mensaje",
            "tipo": "info",
            "usuario_id": "user-123"
        }
        client.post(
            "/api/v1/notificaciones",
            json=create_data,
            headers=auth_headers(admin_token)
        )

        # Listar
        response = client.get(
            "/api/v1/notificaciones/usuario/user-123",
            headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        assert len(response.json()) >= 1
```

## Ventajas de TDD

### 1. Confianza en el Código
- Sabes que tu código funciona antes de enviarlo
- Los tests documentan el comportamiento esperado
- Cambios futuros no rompen funcionalidad existente

### 2. Mejor Diseño
- TDD te obliga a pensar en la API antes de implementar
- Código más modular y testeaable
- Interfaces más claras

### 3. Menos Bugs
- Detectas problemas temprano
- Cobertura completa de casos
- Regresiones detectadas inmediatamente

### 4. Documentación Viva
- Los tests muestran cómo usar el código
- Ejemplos prácticos de cada función
- Se mantienen actualizados (o fallan)

## Checklist TDD

Antes de escribir código nuevo:

- [ ] ¿Escribí el test primero?
- [ ] ¿El test falla por la razón correcta?
- [ ] ¿Escribí el código mínimo necesario?
- [ ] ¿El test pasa ahora?
- [ ] ¿Refactoricé manteniendo tests verdes?
- [ ] ¿Agregué tests para casos edge?
- [ ] ¿La cobertura es >= 80%?

## Comandos Útiles

```bash
# Ejecutar un test específico mientras desarrollas
pytest tests/test_notificaciones.py::TestNotificaciones::test_create_notificacion -v

# Ejecutar con auto-reload (requiere pytest-watch)
ptw tests/test_notificaciones.py

# Ver solo el primer fallo y parar
pytest -x tests/test_notificaciones.py

# Modo verbose con stdout
pytest -v -s tests/test_notificaciones.py
```

## Patrón AAA (Arrange-Act-Assert)

Estructura tus tests siguiendo AAA:

```python
def test_ejemplo(self, client, admin_token, auth_headers):
    """Test siguiendo patrón AAA"""

    # ARRANGE - Preparar datos y contexto
    data = {
        "titulo": "Test",
        "mensaje": "Mensaje"
    }
    headers = auth_headers(admin_token)

    # ACT - Ejecutar la acción
    response = client.post("/api/v1/endpoint", json=data, headers=headers)

    # ASSERT - Verificar resultados
    assert response.status_code == 201
    assert response.json()["titulo"] == "Test"
```

## Tipos de Tests

### 1. Tests Unitarios
Prueban una función/método aislado:

```python
def test_hash_password():
    """Test unitario de función de hash"""
    from app.modules.auth.utils import hash_password

    hashed = hash_password("password123")

    assert hashed != "password123"
    assert len(hashed) > 0
```

### 2. Tests de Integración
Prueban múltiples componentes juntos:

```python
@pytest.mark.integration
def test_create_proyecto_and_add_costo(client, admin_token, auth_headers):
    """Test de integración: crear proyecto y agregar costo"""

    # Crear proyecto
    proyecto_data = {...}
    proyecto = client.post("/api/v1/proyectos", json=proyecto_data).json()

    # Agregar costo al proyecto
    costo_data = {"proyecto_id": proyecto["id"], ...}
    costo = client.post("/api/v1/costos", json=costo_data).json()

    # Verificar que el costo está asociado
    assert costo["proyecto_id"] == proyecto["id"]
```

### 3. Tests End-to-End
Prueban flujos completos de usuario:

```python
@pytest.mark.e2e
def test_flujo_completo_proyecto(client):
    """Test E2E: flujo completo de gestión de proyecto"""

    # 1. Registrar usuario
    user = client.post("/api/v1/auth/register", json={...}).json()

    # 2. Login
    token = client.post("/api/v1/auth/login", json={...}).json()["access_token"]

    # 3. Crear proyecto
    proyecto = client.post("/api/v1/proyectos", json={...}).json()

    # 4. Agregar costos
    costo = client.post("/api/v1/costos", json={...}).json()

    # 5. Validar costo
    validated = client.post(f"/api/v1/costos/{costo['id']}/validar", json={...}).json()

    # 6. Ver resumen financiero
    resumen = client.get(f"/api/v1/proyectos/{proyecto['id']}/resumen").json()

    assert resumen["total_gastado"] > 0
```

## Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [TDD by Example - Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

## Ejercicio Práctico

Implementa el endpoint `GET /api/v1/proyectos/{id}/timeline` usando TDD:

1. Escribe el test primero
2. Haz que falle
3. Implementa lo mínimo
4. Haz que pase
5. Refactoriza
6. Agrega más casos de prueba

¡Practica el ciclo Red-Green-Refactor!
