"""
Schemas de Pydantic para el módulo de Autenticación.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.modules.auth.models import RolUsuario


class UsuarioBase(BaseModel):
    """Schema base de usuario"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    nombre_completo: str = Field(..., min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    rol: RolUsuario = Field(default=RolUsuario.TRABAJADOR)


class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")

    @field_validator('password')
    @classmethod
    def validar_password(cls, v: str) -> str:
        """Valida que la contraseña sea segura"""
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v


class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = Field(None, min_length=1, max_length=200)
    telefono: Optional[str] = Field(None, max_length=20)
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None


class UsuarioResponse(UsuarioBase):
    """Schema de respuesta de usuario"""
    id: str
    telegram_id: Optional[str] = None
    telegram_username: Optional[str] = None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    ultimo_acceso: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "jmartinez",
                "email": "juan@ejemplo.com",
                "nombre_completo": "Juan Martinez",
                "telefono": "+52 1 55 1234 5678",
                "rol": "gerente",
                "telegram_id": "123456789",
                "telegram_username": "jmartinez_tg",
                "activo": True,
                "creado_en": "2025-11-04T10:00:00",
                "actualizado_en": "2025-11-04T10:00:00",
                "ultimo_acceso": "2025-11-04T15:30:00"
            }
        }
    }


class LoginRequest(BaseModel):
    """Schema para login"""
    username: str = Field(..., description="Username o email")
    password: str = Field(..., description="Contraseña")


class TokenResponse(BaseModel):
    """Schema de respuesta de token"""
    access_token: str
    token_type: str = "bearer"
    user: UsuarioResponse


class ChangePasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")

    @field_validator('new_password')
    @classmethod
    def validar_nueva_password(cls, v: str) -> str:
        """Valida que la nueva contraseña sea segura"""
        if len(v) < 6:
            raise ValueError('La nueva contraseña debe tener al menos 6 caracteres')
        return v
