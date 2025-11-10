# Sistema de Gestión de Obras y Costos - Documentación Principal

## 📋 Resumen Ejecutivo

Sistema integral para gestión de proyectos de construcción con enfoque en control financiero y operativo. Diseñado para empresas constructoras que necesitan:

- Control de costos en tiempo real por proyecto
- Captura de datos desde campo vía Telegram
- Dashboards intuitivos para toma de decisiones
- Gestión completa de tareas y asignaciones integrada

## 🎯 Objetivos del Sistema

### Principal

Centralizar y automatizar el control financiero y operativo de proyectos de construcción, eliminando la pérdida de información y mejorando la rentabilidad.

### Específicos

1. **Control Financiero:** Tracking en tiempo real de gastos vs. presupuesto
2. **Eficiencia Operativa:** Captura de datos desde campo sin fricción
3. **Visibilidad Total:** Dashboards con KPIs críticos del negocio
4. **Gestión de Tareas:** Sistema interno completo para manejo de tareas y asignaciones
5. **Trazabilidad:** Registro completo de gastos con evidencia (facturas) y horas trabajadas

## 🏗️ Arquitectura del Sistema

### 🎯 Decisiones Arquitectónicas Tomadas (Nov 2025)

**Base de Datos:**
- **Desarrollo:** SQLite (simple, sin instalación, perfecto para MVP)
- **Producción:** PostgreSQL (migración planificada cuando sea necesario)
- **ORM:** SQLAlchemy con soporte para ambos

**Patrón de Arquitectura Backend:**
- **Estructura Modular por Dominio** (DDD-inspired)
- Cada módulo de negocio (proyectos, costos, tareas) contiene:
  - `models.py`: Modelos SQLAlchemy
  - `schemas.py`: Pydantic schemas (validación)
  - `routes.py`: Endpoints FastAPI
  - `services.py`: Lógica de negocio
  - `repository.py`: Acceso a datos
- Ventajas: Alta cohesión, bajo acoplamiento, fácil de mantener y escalar

**Storage de Archivos:**
- **Desarrollo:** Sistema de archivos local (`uploads/`)
- **Producción:** MinIO (S3-compatible)
- **Implementación:** Abstracción con interface común para intercambiar fácilmente

**Scope MVP Fase 1:**
- ✅ Gestión de Proyectos (CRUD completo)
- ✅ Registro de Gastos (con upload de facturas, sin OCR inicial)
- ⏸️ Sistema de Tareas (Fase 2)
- ⏸️ Registro de Horas (Fase 2)

### Diagrama de Arquitectura General
```mermaid

graph TB
    subgraph "🚶 Usuarios"
        Admin[👔 Administrador/Gerente]
        Field[👷 Personal de Campo]
    end

    subgraph "💻 Capa de Presentación"
        Web[🌐 Web App<br/>React + Vite]
        Bot[💬 Telegram Bot<br/>Interfaz de Campo]
    end

    subgraph "⚙️ Núcleo del Sistema"
        API[🔧 Backend API<br/>FastAPI/Django]
        Cache[(Redis<br/>Cache)]
        DB[(PostgreSQL/SQLite<br/>Base de Datos)]
        Queue[🔄 Celery<br/>Tareas Asíncronas]
    end

    subgraph "🔌 Servicios Locales/Open Source"
        OCR[👁️ Tesseract/EasyOCR<br/>Procesamiento Facturas]
        STT[🎤 Whisper/wav2vec2<br/>Voz a Texto]
        Storage[💾 MinIO/Local<br/>Almacenamiento]
    end

    Admin --> Web
    Field --> Bot

    Web <-->|REST API| API
    Bot <-->|Webhooks| API

    API <--> Cache
    API <--> DB
    API <--> Queue
    Queue --> OCR
    Queue --> STT
    API --> Storage

    style API fill:#ff9999
    style DB fill:#99ccff
    style Web fill:#99ff99
    style Bot fill:#99ff99
```

```

```

## 📊 KPIs y Dashboards Críticos

### 1. Dashboard Ejecutivo (Vista Principal)

```
┌─────────────────────────────────────────────────────┐
│  RESUMEN HOY                                        │
├──────────────┬──────────────┬──────────────────────┤
│ 💰 Gastado   │ 📈 Margen    │ ⚠️ Alertas          │
│ $45,230      │ 23.5%        │ 3 presupuestos      │
│              │              │   excedidos         │
├──────────────┼──────────────┼──────────────────────┤
│ 👷 Personal  │ 📋 Tareas    │ ⏱️ Horas Hoy        │
│ 12 activos   │ 8 pendientes │ 96h registradas     │
└──────────────┴──────────────┴──────────────────────┘
```

**KPIs Principales:**

- **Flujo de Caja Diario:** Ingresos - Egresos del día
- **Burn Rate por Proyecto:** Velocidad de gasto vs. tiempo restante
- **ROI por Proyecto:** (Ganancia / Inversión) × 100
- **Índice de Desempeño de Costos (CPI):** Valor Ganado / Costo Real
- **Productividad Laboral:** Horas trabajadas vs. Horas presupuestadas

### 2. Dashboard de Control de Costos

- **Análisis de Varianza:** Comparación presupuesto vs. real con semáforo
- **Matriz de Gastos:** Heatmap de gastos por categoría y proyecto
- **Proyección de Costos:** Estimación de costo final basado en tendencia actual
- **Top 10 Proveedores:** Por volumen de compra
- **Costo de Mano de Obra:** Por proyecto y trabajador

### 3. Dashboard Operativo

- **Pipeline de Ventas:** Valor total en cada etapa del embudo
- **Utilización de Personal:** % de tiempo productivo por empleado
- **Velocidad de Proyectos:** Tiempo promedio por fase
- **Tablero Kanban de Tareas:** Vista estilo Trello integrada
- **Calendario de Tareas:** Vista mensual de actividades programadas
- **Matriz de Asignación:** Qué empleado está en qué proyecto

## 💾 Modelo de Datos Optimizado

```mermaid
erDiagram
    PROYECTO ||--o{ COSTO : tiene
    PROYECTO ||--o{ TAREA : contiene
    PROYECTO ||--o{ PRESUPUESTO_LINEA : define
    PROYECTO ||--o{ REGISTRO_HORAS : registra
    PERSONAL ||--o{ ASIGNACION : participa
    PERSONAL ||--o{ COSTO : reporta
    PERSONAL ||--o{ REGISTRO_HORAS : trabaja
    TAREA ||--o{ ASIGNACION : requiere
    PROVEEDOR ||--o{ COSTO : suministra
  
    PROYECTO {
        uuid id PK
        string codigo UK
        string nombre
        string cliente
        date fecha_inicio
        date fecha_fin_estimada
        decimal presupuesto_total
        decimal horas_presupuestadas
        enum estado
        json metadata
    }
  
    TAREA {
        uuid id PK
        uuid proyecto_id FK
        string titulo
        text descripcion
        date fecha_programada
        enum prioridad
        enum estado
        uuid asignado_a FK
        timestamp creada_en
        timestamp actualizada_en
    }
  
    COSTO {
        uuid id PK
        uuid proyecto_id FK
        uuid personal_id FK
        uuid proveedor_id FK
        enum categoria
        decimal monto
        string factura_url
        text descripcion
        timestamp fecha_gasto
        boolean validado
        string metodo_captura
    }
  
    REGISTRO_HORAS {
        uuid id PK
        uuid proyecto_id FK
        uuid personal_id FK
        decimal horas
        date fecha
        text descripcion
        timestamp registrado_en
        uuid registrado_por FK
    }
  
    PRESUPUESTO_LINEA {
        uuid id PK
        uuid proyecto_id FK
        enum categoria
        decimal monto_presupuestado
        decimal monto_gastado
        decimal porcentaje_alerta
    }
```

## 🔄 Flujos de Trabajo Principales

### Flujo 1: Captura de Gasto desde Campo

```mermaid
sequenceDiagram
    participant T as 👷 Trabajador
    participant Bot as 🤖 Telegram Bot
    participant API as 🔧 Backend
    participant OCR as 👁️ OCR Service
    participant DB as 💾 Database
    participant N as 📱 Notificaciones

    T->>Bot: 📸 Foto de factura
    Bot->>Bot: Mostrar botones: [Proyecto A] [Proyecto B]
    T->>Bot: Selecciona proyecto
    Bot->>API: Webhook con imagen + proyecto
    API->>OCR: Procesar imagen (Tesseract/EasyOCR)
    OCR-->>API: Datos extraídos
    API->>API: Validar datos
    API->>DB: Guardar gasto
    API->>Bot: Confirmación con datos
    Bot->>T: "Detecté $150 en Home Depot ✅❌"
    T->>Bot: ✅ Confirmar
    API->>N: Notificar si excede presupuesto
    N-->>T: ⚠️ Alerta de presupuesto
```

### Flujo 2: Consulta de Tareas Diarias

```mermaid
sequenceDiagram
    participant T as 👷 Trabajador
    participant Bot as 🤖 Telegram Bot
    participant API as 🔧 Backend
    participant DB as 💾 Database

    T->>Bot: "Tareas pendientes hoy"
    Bot->>API: Solicitud de tareas del día
    API->>DB: Query tareas fecha=hoy, usuario=T
    DB-->>API: Lista de tareas agrupadas
    API->>Bot: Formato de respuesta
    Bot->>T: 📋 Tareas para hoy:<br/>🏗️ Proyecto Casa #23:<br/>• Comprar pintura<br/>• Instalar ventanas<br/>🏗️ Proyecto Local Comercial:<br/>• Llevar pulidora<br/>• Revisar instalación eléctrica
```

### Flujo 3: Agregar Nueva Tarea

```mermaid
sequenceDiagram
    participant T as 👷 Trabajador/Admin
    participant Bot as 🤖 Telegram Bot
    participant API as 🔧 Backend
    participant DB as 💾 Database

    T->>Bot: /nueva_tarea
    Bot->>T: Selecciona proyecto:<br/>[Casa #23] [Local] [Oficina]
    T->>Bot: Selecciona "Casa #23"
    Bot->>T: Escribe la descripción de la tarea:
    T->>Bot: "Instalar griferías en baños"
    Bot->>T: ¿Para cuándo?<br/>[Hoy] [Mañana] [Otra fecha]
    T->>Bot: Selecciona "Mañana"
    Bot->>API: Crear tarea con datos
    API->>DB: INSERT tarea
    DB-->>API: Tarea creada ID#456
    API->>Bot: Confirmación
    Bot->>T: ✅ Tarea agregada para mañana
```

### Flujo 4: Registro de Horas Trabajadas

```mermaid
sequenceDiagram
    participant S as 👔 Supervisor
    participant Bot as 🤖 Telegram Bot
    participant API as 🔧 Backend
    participant DB as 💾 Database

    S->>Bot: /registrar_horas
    Bot->>S: Selecciona trabajador:<br/>[Juan] [Pedro] [María] [Luis]
    S->>Bot: Selecciona "Juan"
    Bot->>S: Selecciona proyecto:<br/>[Casa #23] [Local] [Oficina]
    S->>Bot: Selecciona "Casa #23"
    Bot->>S: ¿Cuántas horas trabajó?<br/>[4] [6] [8] [Otra cantidad]
    S->>Bot: Selecciona "8"
    Bot->>API: Registrar horas
    API->>DB: INSERT registro_horas
    API->>DB: UPDATE proyecto costos_mano_obra
    DB-->>API: Registro exitoso
    API->>Bot: Confirmación
    Bot->>S: ✅ 8 horas registradas<br/>Juan en Casa #23<br/>Total horas proyecto: 156/200
```

### Flujo 5: Actualización de Progreso con Voz

```mermaid
sequenceDiagram
    participant T as 👷 Trabajador
    participant Bot as 🤖 Telegram Bot
    participant API as 🔧 Backend
    participant STT as 🎤 Speech-to-Text
    participant DB as 💾 Database

    T->>Bot: 🎤 "Terminamos instalación eléctrica en Casa 23"
    Bot->>API: Audio file
    API->>STT: Transcribir (Whisper/wav2vec2)
    STT-->>API: Texto transcrito
    API->>API: NLP para extraer proyecto y acción
    API->>DB: Actualizar tarea estado="completado"
    DB-->>API: Tarea actualizada
    API->>Bot: Confirmación
    Bot->>T: "✅ Tarea 'Instalación eléctrica' completada"
```

## 🚀 Plan de Implementación (MVP)

### Fase 1: Fundación (2 semanas)

- [ ] Setup del repositorio y CI/CD
- [ ] Configuración de base de datos (PostgreSQL o SQLite para desarrollo)
- [ ] API básica con FastAPI y autenticación JWT
- [ ] Bot de Telegram básico (registro de usuarios)
- [ ] Configuración de MinIO para almacenamiento local

### Fase 2: Core Features (3 semanas)

- [ ] CRUD de Proyectos y Presupuestos
- [ ] Sistema de captura de gastos manual
- [ ] Dashboard básico de costos
- [ ] Sistema de gestión de tareas integrado
- [ ] Registro de horas trabajadas
- [ ] Consulta de tareas diarias vía Telegram

### Fase 3: Inteligencia (2 semanas)

- [ ] Integración Tesseract/EasyOCR para facturas
- [ ] Whisper para transcripción de voz
- [ ] Sistema de alertas automáticas
- [ ] Reportes PDF exportables con ReportLab

### Fase 4: Optimización (1 semana)

- [ ] Cache con Redis
- [ ] Optimización de queries
- [ ] PWA para acceso móvil
- [ ] Tests de carga con Locust

## 🛠️ Stack Tecnológico Recomendado

### Backend (Python)

```yaml
Core:
  - Framework: FastAPI o Django REST Framework
  - Database: PostgreSQL (producción) / SQLite (desarrollo)
  - Cache: Redis (opcional para MVP)
  - Queue: Celery + Redis/RabbitMQ
  - ORM: SQLAlchemy (FastAPI) o Django ORM

Librerías Clave:
  - Auth: python-jose[cryptography] para JWT
  - Validación: Pydantic
  - Telegram Bot: python-telegram-bot
  - Testing: pytest + pytest-asyncio
  - Migrations: Alembic (FastAPI) o Django migrations
```

### Servicios Open Source / Locales

```yaml
OCR:
  - Tesseract OCR (más maduro, mejor para facturas)
  - EasyOCR (mejor para texto manuscrito)
  - PaddleOCR (buena alternativa)

Speech-to-Text:
  - OpenAI Whisper (local, muy preciso)
  - wav2vec2 (Facebook/Meta, rápido)
  - SpeechRecognition (múltiples backends)

Almacenamiento:
  - MinIO (S3-compatible, self-hosted)
  - Sistema de archivos local con nginx
  - Nextcloud (si necesitas más features)

Base de Datos Alternativas:
  - PostgreSQL (recomendado, robusto)
  - SQLite (perfecto para empezar, un solo archivo)
  - MariaDB/MySQL (alternativa popular)
```

### Frontend

```yaml
Framework: React 18 + Vite
State Management: Zustand (simple) o Redux Toolkit
UI Components: 
  - Ant Design (completo)
  - Mantine (moderno)
  - Tailwind UI (si prefieres Tailwind)
Charts: Recharts + D3.js
Forms: React Hook Form + Yup/Zod
PWA: Vite PWA Plugin
```

### Infraestructura para Deployment

```yaml
Opción 1 - Servidor Local:
  - Reverse Proxy: nginx o Caddy (auto-HTTPS)
  - Contenedores: Docker + Docker Compose
  - Backup: rsync + cron
  - Monitoreo: Prometheus + Grafana
  - DynDNS: DuckDNS o No-IP (para IP dinámica)

Opción 2 - VPS Económico:
  - Proveedores: DigitalOcean ($4-6/mes), Vultr, Linode
  - OS: Ubuntu 22.04 LTS
  - Deployment: Docker Compose + GitHub Actions
  - SSL: Let's Encrypt con Certbot
  - Backup: Snapshots del VPS + pg_dump

Opción 3 - Híbrido (Recomendado):
  - Frontend: Vercel/Netlify (gratis)
  - Backend API: VPS económico
  - Base de Datos: PostgreSQL en VPS
  - Almacenamiento: MinIO en servidor local
  - Backup: Múltiples ubicaciones
```

## 📱 Comandos del Bot de Telegram

### Comandos Básicos

```
/start - Iniciar y registrar usuario
/proyecto - Seleccionar proyecto activo
/gasto - Reportar un gasto
/tareas - Ver tareas del día
/nueva_tarea - Agregar una tarea
/horas - Registrar horas trabajadas
/avance - Reportar avance de tarea
/resumen - Ver resumen del día
/ayuda - Mostrar comandos disponibles
```

### Flujo de Interacción Optimizado

#### Consulta de Tareas Diarias

```
👷: /tareas
🤖: 📋 Tareas para hoy (26 Oct):

🏗️ Casa Martinez #23:
  ⚡ Comprar pintura blanca (Alta prioridad)
  ⚡ Instalar ventanas sala (Media)
  
🏗️ Local Comercial Centro:
  ⚡ Llevar pulidora (Alta)
  ⚡ Revisar instalación eléctrica (Media)

[Ver mañana] [Ver semana] [Filtrar proyecto]
```

#### Reporte de Gasto

```
👷: /gasto
🤖: ¿Cómo quieres reportar el gasto?
    [📸 Foto] [✍️ Manual] [🎤 Voz]

👷: [📸 Foto]
🤖: Envía la foto de la factura

👷: *envía foto*
🤖: Procesando... 
    Detecté: $1,250.00 - Home Depot
    Proyecto: Reforma Cocina Casa #23
  
    [✅ Confirmar] [✏️ Editar] [❌ Cancelar]
```

#### Registro de Horas Trabajadas

```
👔: /horas
🤖: Selecciona el trabajador:
  
    [👷 Juan Pérez]
    [👷 María García] 
    [👷 Pedro López]
    [➕ Varios trabajadores]

👔: [Juan Pérez]
🤖: ¿En qué proyecto trabajó?
  
    [🏗️ Casa #23]
    [🏗️ Local Centro]
    [🏗️ Oficina Norte]

👔: [Casa #23]
🤖: ¿Cuántas horas?
  
    [4 horas] [6 horas] [8 horas] 
    [10 horas] [Otra cantidad]

👔: [8 horas]
🤖: ✅ Registrado:
    Juan Pérez - 8 horas
    Proyecto: Casa #23
    Fecha: 26 Oct 2025
  
    💰 Costo mano obra: $160
    📊 Total horas proyecto: 156/200 (78%)
```

#### Agregar Nueva Tarea

```
👷: /nueva_tarea
🤖: ¿Para qué proyecto?
  
    [🏗️ Casa #23]
    [🏗️ Local Centro]
    [🏗️ Ver todos...]

👷: [Casa #23]
🤖: Describe la tarea:

👷: Instalar griferías en baños principales
🤖: ¿Cuándo debe realizarse?
  
    [📅 Hoy]
    [📅 Mañana]
    [📅 Esta semana]
    [📅 Elegir fecha]

👷: [Mañana]
🤖: ¿Prioridad?
  
    [🔴 Alta] [🟡 Media] [🟢 Baja]

👷: [🔴 Alta]
🤖: ✅ Tarea creada:
    "Instalar griferías en baños principales"
    📅 Mañana 27 Oct
    🔴 Prioridad Alta
    🏗️ Casa #23
```

## 🗄️ Comparación de Bases de Datos

### PostgreSQL vs SQLite vs MariaDB

| Característica            | PostgreSQL         | SQLite                | MariaDB           |
| -------------------------- | ------------------ | --------------------- | ----------------- |
| **Instalación**     | Requiere servidor  | Un archivo            | Requiere servidor |
| **Concurrencia**     | Excelente          | Limitada (escrituras) | Muy buena         |
| **Tamaño máximo**  | Sin límite        | 281 TB                | Sin límite       |
| **RAM requerida**    | ~256MB mínimo     | Mínima (~10MB)       | ~256MB mínimo    |
| **Backup**           | pg_dump, streaming | Copiar archivo        | mysqldump         |
| **JSON nativo**      | ✅ Excelente       | ✅ Básico            | ✅ Bueno          |
| **Full-text search** | ✅ Potente         | ✅ Básico            | ✅ Bueno          |
| **Replicación**     | ✅ Nativa          | ❌ Manual             | ✅ Nativa         |
| **Ideal para**       | Producción        | MVP/Desarrollo        | Producción       |

### Recomendación por Etapa

```python
# Configuración por ambiente en FastAPI
import os
from sqlalchemy import create_engine

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "development":
    # SQLite para desarrollo local - Simple y sin configuración
    DATABASE_URL = "sqlite:///./obras.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ Usando SQLite - Perfecto para desarrollo")

elif ENVIRONMENT == "staging":
    # PostgreSQL local para pruebas
    DATABASE_URL = "postgresql://obras:password@localhost/obras_staging"
    engine = create_engine(DATABASE_URL)
    print("✅ Usando PostgreSQL local - Pruebas realistas")

else:  # production
    # PostgreSQL en producción
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10)
    print("✅ Usando PostgreSQL en producción")
```

### Migración de SQLite a PostgreSQL

```bash
# Script de migración cuando estés listo para producción
#!/bin/bash

# 1. Exportar datos de SQLite
sqlite3 obras.db .dump > dump.sql

# 2. Convertir sintaxis SQLite a PostgreSQL
sed -i 's/AUTOINCREMENT/SERIAL/g' dump.sql
sed -i 's/datetime/timestamp/g' dump.sql
sed -i 's/PRAGMA.*;//g' dump.sql

# 3. Importar a PostgreSQL
createdb obras_prod
psql obras_prod < dump.sql

echo "✅ Migración completada"
```

### Configuración Óptima para VPS Pequeño

```yaml
# PostgreSQL - postgresql.conf para VPS con 2GB RAM
shared_buffers = 256MB          # 25% de RAM
effective_cache_size = 1GB      # 50% de RAM
maintenance_work_mem = 64MB
work_mem = 4MB
max_connections = 50            # Suficiente para app pequeña

# SQLite - Configuración Python
import sqlite3

def get_sqlite_connection():
    conn = sqlite3.connect('obras.db', timeout=20)
    # Optimizaciones para SQLite
    conn.execute("PRAGMA journal_mode=WAL")        # Mejor concurrencia
    conn.execute("PRAGMA synchronous=NORMAL")      # Balance velocidad/seguridad
    conn.execute("PRAGMA cache_size=10000")        # Cache en memoria
    conn.execute("PRAGMA temp_store=MEMORY")       # Temp en RAM
    return conn
```

## 💰 Consideraciones de Costos y Recursos

### Opción 1: Servidor Local (Más económico a largo plazo)

```yaml
Hardware Mínimo:
  - CPU: 4 cores
  - RAM: 8GB (mínimo), 16GB (recomendado)
  - Almacenamiento: 100GB SSD
  - Internet: IP fija o DynDNS

Costos:
  - Hardware: ~$300-500 (una sola vez)
  - Internet: Tu plan actual + IP fija (~$10-20/mes extra)
  - Dominio: ~$12/año
  - SSL: Gratis con Let's Encrypt
  - Total mensual: ~$10-20

Ventajas:
  - Control total
  - Sin límites de almacenamiento
  - Procesamiento OCR/STT ilimitado
  - Datos 100% privados
```

### Opción 2: VPS Económico

```yaml
Proveedores y Precios:
  DigitalOcean:
    - Droplet básico: $4-6/mes (1GB RAM, 25GB SSD)
    - Recomendado: $12/mes (2GB RAM, 50GB SSD)
  
  Vultr:
    - Cloud Compute: $5/mes (1GB RAM, 25GB SSD)
    - High Frequency: $6/mes (1GB RAM, 32GB SSD)
  
  Hetzner:
    - CX11: €3.29/mes (~$3.5) (2GB RAM, 20GB SSD)
    - Mejor relación precio/rendimiento

Costos adicionales:
  - Dominio: ~$12/año
  - Backups: ~$1-2/mes
  - Total mensual: ~$6-15

Limitaciones:
  - Almacenamiento limitado
  - Procesamiento OCR/STT puede ser lento
  - Necesitas gestionar backups
```

### Opción 3: Híbrido (Recomendado)

```yaml
Arquitectura:
  - Frontend: Vercel/Netlify (gratis hasta 100GB bandwidth)
  - Backend API: VPS económico ($5-6/mes)
  - Base de datos: PostgreSQL en VPS
  - Almacenamiento pesado: Servidor local con túnel
  - OCR/STT: Procesamiento local

Costos mensuales:
  - VPS: $5-6
  - Túnel (Cloudflare Tunnel): Gratis
  - Total: ~$5-6/mes

Ventajas:
  - Frontend rápido y global
  - Backend escalable
  - Procesamiento pesado local
  - Costos mínimos
```

### Recursos Gratuitos Disponibles

```yaml
Estudiantes/Startups:
  - GitHub Student Pack: $200 créditos DigitalOcean
  - AWS Activate: Hasta $5000 créditos
  - Google Cloud: $300 créditos primer año
  - Azure: $100 créditos

Servicios Always Free:
  - Cloudflare Tunnel: Exponer servidor local
  - Railway: 500 horas/mes gratis
  - Render: Apps estáticas gratis
  - Supabase: PostgreSQL gratis (500MB)
```

## 🔐 Consideraciones de Seguridad

1. **Autenticación Multi-factor** para acceso web
2. **Encriptación** de datos sensibles (AES-256)
3. **Rate Limiting** en todas las APIs
4. **Validación de Telegram ID** para evitar suplantación
5. **Backup automático** cada 6 horas
6. **Logs de auditoría** para todas las transacciones

## 📈 Métricas de Éxito

### Técnicas

- Tiempo de respuesta API < 200ms (p95)
- Disponibilidad > 99.9%
- Procesamiento OCR > 95% precisión

### Negocio

- Reducción 30% en tiempo de captura de datos
- Mejora 25% en margen de proyectos
- 100% trazabilidad de gastos

## 🔄 Mejoras Futuras (Post-MVP)

1. **IA Predictiva:** Alertas tempranas de sobrecostos
2. **App Móvil Nativa:** iOS/Android con funcionalidad offline
3. **Integración Bancaria:** Conciliación automática
4. **Marketplace de Proveedores:** Comparación de precios
5. **Módulo de Facturación:** Generación automática de facturas
6. **Analytics Avanzado:** Machine Learning para optimización

## 📝 Notas de Implementación

### Manejo de Estados y Categorías

```python
# Estados de Proyecto
class EstadoProyecto(Enum):
    PROSPECTO = 'prospecto'
    COTIZACION = 'cotizacion'
    APROBADO = 'aprobado'
    EN_PROGRESO = 'en_progreso'
    PAUSADO = 'pausado'
    COMPLETADO = 'completado'
    CANCELADO = 'cancelado'

# Estados de Tarea
class EstadoTarea(Enum):
    PENDIENTE = 'pendiente'
    EN_PROGRESO = 'en_progreso'
    COMPLETADA = 'completada'
    CANCELADA = 'cancelada'
    POSPUESTA = 'pospuesta'

# Prioridades de Tarea
class PrioridadTarea(Enum):
    ALTA = 'alta'
    MEDIA = 'media'
    BAJA = 'baja'

# Categorías de Gastos
class CategoriaGasto(Enum):
    MATERIALES = 'materiales'
    MANO_OBRA = 'mano_obra'
    TRANSPORTE = 'transporte'
    HERRAMIENTAS = 'herramientas'
    SUBCONTRATO = 'subcontrato'
    OTROS = 'otros'
```

### Webhooks de Telegram con FastAPI

```python
from fastapi import FastAPI, HTTPException
from telegram import Update
from telegram.ext import Application
import hmac
import hashlib

app = FastAPI()
bot_app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

@app.post("/telegram/webhook")
async def telegram_webhook(update: dict):
    # Verificar firma del webhook (opcional pero recomendado)
    if not verify_telegram_signature(update):
        raise HTTPException(status_code=401, detail="Unauthorized")
  
    # Convertir a objeto Update de python-telegram-bot
    telegram_update = Update.de_json(update, bot_app.bot)
  
    # Procesar según tipo de mensaje
    if telegram_update.message:
        if telegram_update.message.photo:
            await process_expense_photo(telegram_update)
        elif telegram_update.message.voice:
            await process_voice_update(telegram_update)
        elif telegram_update.message.text:
            await process_text_command(telegram_update)
    elif telegram_update.callback_query:
        await process_callback_query(telegram_update)
  
    return {"ok": True}

# Procesamiento de imagen con OCR local
async def process_expense_photo(update: Update):
    """Procesar foto de factura con Tesseract/EasyOCR"""
    # Descargar imagen
    file = await update.message.photo[-1].get_file()
    image_bytes = await file.download_as_bytearray()
  
    # Guardar temporalmente
    temp_path = f"/tmp/{update.message.message_id}.jpg"
    with open(temp_path, "wb") as f:
        f.write(image_bytes)
  
    # Procesar con OCR
    if OCR_ENGINE == "tesseract":
        import pytesseract
        text = pytesseract.image_to_string(temp_path, lang='spa+eng')
    else:  # easyocr
        import easyocr
        reader = easyocr.Reader(['es', 'en'])
        result = reader.readtext(temp_path)
        text = ' '.join([item[1] for item in result])
  
    # Extraer datos de la factura
    expense_data = parse_expense_from_text(text)
  
    # Confirmar con el usuario
    keyboard = [
        [InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm_expense_{update.message.message_id}")],
        [InlineKeyboardButton("✏️ Editar", callback_data=f"edit_expense_{update.message.message_id}")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancel_expense")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
  
    await update.message.reply_text(
        f"Detecté:\n"
        f"💰 Monto: ${expense_data['amount']}\n"
        f"🏪 Proveedor: {expense_data['vendor']}\n"
        f"📅 Fecha: {expense_data['date']}\n"
        f"🏗️ Proyecto: {expense_data['project']}",
        reply_markup=reply_markup
    )

# Procesamiento de voz con Whisper
async def process_voice_update(update: Update):
    """Procesar mensaje de voz con Whisper"""
    # Descargar audio
    file = await update.message.voice.get_file()
    audio_bytes = await file.download_as_bytearray()
  
    # Guardar temporalmente
    temp_path = f"/tmp/{update.message.message_id}.ogg"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)
  
    # Transcribir con Whisper
    import whisper
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(temp_path, language="es")
    text = result["text"]
  
    # Analizar intención y extraer información
    intent_data = analyze_voice_intent(text)
  
    # Responder según la intención detectada
    if intent_data["intent"] == "task_complete":
        await mark_task_complete(update, intent_data)
    elif intent_data["intent"] == "report_progress":
        await save_progress_note(update, intent_data)
    else:
        await update.message.reply_text(
            f"📝 Entendí: '{text}'\n"
            "¿Qué deseas hacer con esta información?"
        )
```

### Configuración de MinIO para almacenamiento

```python
from minio import Minio
from minio.error import S3Error

# Cliente MinIO
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False  # True si usas HTTPS
)

# Crear bucket si no existe
def setup_minio():
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
            print(f"Bucket {MINIO_BUCKET} creado")
    except S3Error as e:
        print(f"Error configurando MinIO: {e}")

# Subir archivo
async def upload_to_minio(file_path: str, object_name: str):
    """Subir archivo a MinIO y retornar URL"""
    try:
        minio_client.fput_object(
            MINIO_BUCKET,
            object_name,
            file_path,
        )
        # Generar URL presigned (válida por 7 días)
        url = minio_client.presigned_get_object(
            MINIO_BUCKET,
            object_name,
            expires=timedelta(days=7)
        )
        return url
    except S3Error as e:
        logger.error(f"Error subiendo a MinIO: {e}")
        return None
```

### Script de Setup Inicial

```bash
#!/bin/bash
# setup.sh - Script de configuración inicial

echo "🚀 Configurando Sistema de Gestión de Obras"

# Crear estructura de directorios
mkdir -p backend/{app,tests,migrations}
mkdir -p frontend/{src,public}
mkdir -p bot/{handlers,keyboards}
mkdir -p docker
mkdir -p uploads/{facturas,temp}

# Crear ambiente virtual Python
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias backend
pip install fastapi uvicorn sqlalchemy alembic
pip install python-telegram-bot redis celery
pip install pytesseract easyocr openai-whisper
pip install minio python-multipart
pip install pytest pytest-asyncio

# Configurar base de datos
echo "Configurando base de datos..."
createdb obras

# Inicializar Alembic
cd backend
alembic init migrations

echo "✅ Setup completo! Revisa el archivo .env.example"
```

## 🤝 Contribución y Soporte

### Estructura de Carpetas

```
proyecto-obras/
├── backend/
│   ├── src/
│   │   ├── modules/
│   │   ├── services/
│   │   ├── utils/
│   │   └── config/
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   └── public/
├── bot/
│   ├── handlers/
│   ├── keyboards/
│   └── utils/
├── docker/
├── docs/
└── scripts/
```

### Variables de Entorno Requeridas

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/obras
# Para SQLite: sqlite:///./obras.db

# APIs
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_WEBHOOK_URL=https://tu-dominio.com/telegram/webhook

# Security
JWT_SECRET=xxx
ENCRYPTION_KEY=xxx
ALLOWED_ORIGINS=http://localhost:3000,https://tu-dominio.com

# Storage (MinIO o Local)
STORAGE_TYPE=minio  # o 'local'
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=obras-facturas

# OCR Settings
OCR_ENGINE=tesseract  # o 'easyocr'
TESSERACT_PATH=/usr/bin/tesseract
OCR_LANGUAGES=spa,eng

# Speech-to-Text
STT_ENGINE=whisper  # o 'wav2vec2'
WHISPER_MODEL=base  # tiny, base, small, medium, large
WHISPER_DEVICE=cpu  # o 'cuda' si tienes GPU

# Workers
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Application
DEBUG=False
ENVIRONMENT=production  # development, staging, production
MAX_FILE_SIZE=10485760  # 10MB en bytes
```

### Configuración Docker Compose para Desarrollo

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: obras
      POSTGRES_USER: obras_user
      POSTGRES_PASSWORD: obras_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://obras_user:obras_pass@db:5432/obras
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: minio:9000
    depends_on:
      - db
      - redis
      - minio
    volumes:
      - ./backend:/app
      - ./uploads:/app/uploads
    ports:
      - "8000:8000"

  celery:
    build: ./backend
    command: celery -A app.celery worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://obras_user:obras_pass@db:5432/obras
      CELERY_BROKER_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    environment:
      VITE_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  minio_data:
```

---

## 📚 Referencias y Recursos

### Documentación de Herramientas Open Source

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [MinIO Documentation](https://docs.min.io/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [SQLite When to Use](https://www.sqlite.org/whentouse.html)

### Recursos de Deployment

- [DigitalOcean $200 Credit](https://www.digitalocean.com/github-students)
- [Vultr Free Trial](https://www.vultr.com/promo/)
- [Caddy Server (Auto-HTTPS)](https://caddyserver.com/)
- [DuckDNS (Dynamic DNS)](https://www.duckdns.org/)

### Tutoriales Recomendados

- [Deploy FastAPI with Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Self-hosting MinIO](https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-single-drive.html)
- [Whisper API Local Setup](https://github.com/ahmetoner/whisper-asr-webservice)

---

**Última actualización:** Octubre 2025
**Versión:** 2.0.0
**Autor:** Sistema de Gestión de Obras - Equipo de Desarrollo
