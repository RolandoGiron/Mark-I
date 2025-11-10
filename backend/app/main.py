"""
Aplicación principal de FastAPI.
Entry point del sistema Mark-I.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base

# Importar routers
from app.modules.auth.routes import router as auth_router
from app.modules.proyectos.routes import router as proyectos_router
from app.modules.costos.routes import router as costos_router
from app.modules.personal.routes import router as personal_router
from app.modules.tareas.routes import router as tareas_router
from app.modules.horas.routes import router as horas_router
from app.modules.notificaciones.routes import router as notificaciones_router

# Crear tablas en la base de datos (solo para desarrollo)
# En producción se usará Alembic para migraciones
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

# Inicializar aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema integral para gestión de proyectos de construcción con control financiero y operativo",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Endpoint de health check para monitoreo"""
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "health": "/health"
    }


# Incluir routers de módulos
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["Auth"])
app.include_router(proyectos_router, prefix=settings.API_V1_PREFIX, tags=["Proyectos"])
app.include_router(costos_router, prefix=settings.API_V1_PREFIX, tags=["Costos"])
app.include_router(personal_router, prefix=settings.API_V1_PREFIX, tags=["Personal"])
app.include_router(tareas_router, prefix=settings.API_V1_PREFIX, tags=["Tareas"])
app.include_router(horas_router, prefix=settings.API_V1_PREFIX, tags=["Horas"])
app.include_router(notificaciones_router, prefix=settings.API_V1_PREFIX, tags=["Notificaciones"])

# Montar directorio de archivos estáticos (uploads)
import os
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Acciones al iniciar la aplicación"""
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📦 Ambiente: {settings.ENVIRONMENT}")
    print(f"🔗 Base de datos: {settings.DATABASE_URL}")
    print(f"💾 Storage: {settings.STORAGE_TYPE}")


@app.on_event("shutdown")
async def shutdown_event():
    """Acciones al cerrar la aplicación"""
    print(f"👋 Cerrando {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
