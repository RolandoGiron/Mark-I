"""
Configuración de la aplicación usando Pydantic Settings.
Carga variables de entorno desde .env
"""

from typing import List, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # Application
    APP_NAME: str = "Mark-I - Sistema de Gestión de Obras"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./obras.db"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Convierte el string de CORS a lista"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Storage
    STORAGE_TYPE: Literal["local", "minio"] = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB

    # MinIO (cuando STORAGE_TYPE=minio)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "obras-facturas"
    MINIO_SECURE: bool = False

    # Telegram Bot (Fase 2)
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_WEBHOOK_URL: str | None = None

    # OCR Configuration (Fase 3)
    OCR_ENGINE: Literal["tesseract", "easyocr"] | None = None
    TESSERACT_PATH: str = "/usr/bin/tesseract"
    OCR_LANGUAGES: str = "spa,eng"

    # Speech-to-Text (Fase 3)
    STT_ENGINE: Literal["whisper", "wav2vec2"] | None = None
    WHISPER_MODEL: Literal["tiny", "base", "small", "medium", "large"] = "base"
    WHISPER_DEVICE: Literal["cpu", "cuda"] = "cpu"

    # Celery (Fase 2/3)
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    # Redis (Fase 4)
    REDIS_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuración de la aplicación.
    Usa lru_cache para singleton pattern.
    """
    return Settings()


# Exportar settings para uso global
settings = get_settings()
