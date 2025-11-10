"""
Capa de abstracción para almacenamiento de archivos.
Soporta sistema de archivos local y MinIO (S3-compatible).
"""

import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO
from fastapi import UploadFile

from app.config import settings


class StorageService(ABC):
    """Interface abstracta para servicios de almacenamiento"""

    @abstractmethod
    def upload_file(self, file: UploadFile, folder: str, prefix: str = "") -> str:
        """
        Sube un archivo al storage.

        Args:
            file: Archivo a subir
            folder: Carpeta destino
            prefix: Prefijo opcional para el nombre del archivo

        Returns:
            URL o path del archivo subido
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> bool:
        """Elimina un archivo del storage"""
        pass

    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        """Obtiene la URL pública de un archivo"""
        pass

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Verifica si un archivo existe"""
        pass


class LocalFileStorage(StorageService):
    """Implementación de storage usando sistema de archivos local"""

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def upload_file(self, file: UploadFile, folder: str, prefix: str = "") -> str:
        """Sube un archivo al sistema de archivos local"""
        # Crear carpeta si no existe
        folder_path = self.base_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        # Generar nombre único del archivo
        file_extension = Path(file.filename).suffix
        unique_filename = f"{prefix}{uuid.uuid4()}{file_extension}"
        file_path = folder_path / unique_filename

        # Guardar archivo
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)

        # Retornar path relativo
        relative_path = file_path.relative_to(self.base_dir)
        return str(relative_path)

    def delete_file(self, file_path: str) -> bool:
        """Elimina un archivo del sistema local"""
        try:
            full_path = self.base_dir / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error eliminando archivo {file_path}: {e}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """Retorna la URL para acceder al archivo"""
        # En desarrollo, retorna el path relativo
        # En producción, debería ser servido por nginx o CDN
        return f"/uploads/{file_path}"

    def file_exists(self, file_path: str) -> bool:
        """Verifica si un archivo existe"""
        full_path = self.base_dir / file_path
        return full_path.exists()

    def get_full_path(self, file_path: str) -> Path:
        """Obtiene el path completo de un archivo"""
        return self.base_dir / file_path


class MinIOStorage(StorageService):
    """Implementación de storage usando MinIO (S3-compatible)"""

    def __init__(self):
        from minio import Minio

        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket = settings.MINIO_BUCKET

        # Crear bucket si no existe
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Crea el bucket si no existe"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                print(f"✅ Bucket {self.bucket} creado en MinIO")
        except Exception as e:
            print(f"⚠️ Error verificando/creando bucket: {e}")

    def upload_file(self, file: UploadFile, folder: str, prefix: str = "") -> str:
        """Sube un archivo a MinIO"""
        # Generar nombre único
        file_extension = Path(file.filename).suffix
        unique_filename = f"{prefix}{uuid.uuid4()}{file_extension}"
        object_name = f"{folder}/{unique_filename}"

        # Resetear el cursor del archivo
        file.file.seek(0)

        # Subir a MinIO
        try:
            self.client.put_object(
                self.bucket,
                object_name,
                file.file,
                length=-1,  # Unknown size
                part_size=10*1024*1024,  # 10MB parts
                content_type=file.content_type
            )

            return object_name

        except Exception as e:
            raise Exception(f"Error subiendo archivo a MinIO: {e}")

    def delete_file(self, file_path: str) -> bool:
        """Elimina un archivo de MinIO"""
        try:
            self.client.remove_object(self.bucket, file_path)
            return True
        except Exception as e:
            print(f"Error eliminando archivo de MinIO {file_path}: {e}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """Genera una URL presigned para acceder al archivo"""
        from datetime import timedelta

        try:
            # URL válida por 7 días
            url = self.client.presigned_get_object(
                self.bucket,
                file_path,
                expires=timedelta(days=7)
            )
            return url
        except Exception as e:
            print(f"Error generando URL presigned: {e}")
            return f"/uploads/{file_path}"

    def file_exists(self, file_path: str) -> bool:
        """Verifica si un archivo existe en MinIO"""
        try:
            self.client.stat_object(self.bucket, file_path)
            return True
        except Exception:
            return False


def get_storage_service() -> StorageService:
    """
    Factory para obtener el servicio de storage configurado.

    Returns:
        StorageService: Instancia del servicio según configuración
    """
    if settings.STORAGE_TYPE == "minio":
        return MinIOStorage()
    else:
        return LocalFileStorage()


# Instancia global del storage service
storage_service = get_storage_service()
