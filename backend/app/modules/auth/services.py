"""
Servicios de lógica de negocio para el módulo de Autenticación.
"""

from typing import List, Optional
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario, RolUsuario
from app.modules.auth.schemas import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    LoginRequest,
    TokenResponse,
    ChangePasswordRequest
)
from app.modules.auth.repository import UsuarioRepository
from app.modules.auth.utils import (
    hash_password,
    verify_password,
    create_access_token
)
from app.config import settings


class AuthService:
    """Servicio para lógica de negocio de Autenticación"""

    def __init__(self, db: Session):
        self.repository = UsuarioRepository(db)
        self.db = db

    def register(self, usuario_data: UsuarioCreate) -> UsuarioResponse:
        """Registra un nuevo usuario"""
        # Verificar que username y email no existan
        if self.repository.exists_username(usuario_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El username '{usuario_data.username}' ya está en uso"
            )

        if self.repository.exists_email(usuario_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email '{usuario_data.email}' ya está registrado"
            )

        # Hashear contraseña
        hashed_password = hash_password(usuario_data.password)

        # Crear usuario
        usuario = self.repository.create(usuario_data, hashed_password)

        return self._to_response(usuario)

    def login(self, login_data: LoginRequest) -> TokenResponse:
        """Autentica un usuario y retorna token JWT"""
        # Buscar usuario por username o email
        usuario = self.repository.get_by_username(login_data.username)
        if not usuario:
            usuario = self.repository.get_by_email(login_data.username)

        # Verificar existencia y contraseña
        if not usuario or not verify_password(login_data.password, usuario.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Verificar que esté activo
        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. Contacta al administrador."
            )

        # Actualizar último acceso
        self.repository.update_ultimo_acceso(usuario)

        # Crear token
        access_token = create_access_token(
            data={
                "sub": usuario.id,
                "username": usuario.username,
                "rol": usuario.rol.value
            }
        )

        return TokenResponse(
            access_token=access_token,
            user=self._to_response(usuario)
        )

    def get_usuario_by_id(self, usuario_id: str) -> UsuarioResponse:
        """Obtiene un usuario por ID"""
        usuario = self.repository.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario no encontrado"
            )

        return self._to_response(usuario)

    def get_current_user(self, usuario_id: str) -> Usuario:
        """
        Obtiene el usuario actual (usado por dependency).
        Retorna el modelo completo, no el schema.
        """
        usuario = self.repository.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )

        return usuario

    def get_usuarios(
        self,
        skip: int = 0,
        limit: int = 100,
        rol: Optional[RolUsuario] = None,
        activo: Optional[bool] = None
    ) -> tuple[List[UsuarioResponse], int]:
        """Obtiene lista de usuarios"""
        usuarios, total = self.repository.get_all(
            skip=skip,
            limit=limit,
            rol=rol,
            activo=activo
        )

        return [self._to_response(u) for u in usuarios], total

    def update_usuario(
        self,
        usuario_id: str,
        usuario_data: UsuarioUpdate
    ) -> UsuarioResponse:
        """Actualiza un usuario"""
        usuario = self.repository.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Verificar email si se actualiza
        if usuario_data.email and usuario_data.email != usuario.email:
            if self.repository.exists_email(usuario_data.email, exclude_id=usuario_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El email '{usuario_data.email}' ya está en uso"
                )

        usuario = self.repository.update(usuario, usuario_data)

        return self._to_response(usuario)

    def change_password(
        self,
        usuario_id: str,
        password_data: ChangePasswordRequest
    ) -> dict:
        """Cambia la contraseña de un usuario"""
        usuario = self.repository.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Verificar contraseña actual
        if not verify_password(password_data.current_password, usuario.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )

        # Actualizar contraseña
        new_hashed = hash_password(password_data.new_password)
        self.repository.update_password(usuario, new_hashed)

        return {"message": "Contraseña actualizada exitosamente"}

    def delete_usuario(self, usuario_id: str) -> dict:
        """Elimina un usuario"""
        usuario = self.repository.get_by_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        self.repository.delete(usuario)

        return {"message": f"Usuario {usuario.username} eliminado exitosamente"}

    def _to_response(self, usuario: Usuario) -> UsuarioResponse:
        """Convierte un modelo Usuario a UsuarioResponse"""
        return UsuarioResponse(
            id=usuario.id,
            username=usuario.username,
            email=usuario.email,
            nombre_completo=usuario.nombre_completo,
            telefono=usuario.telefono,
            telegram_id=usuario.telegram_id,
            telegram_username=usuario.telegram_username,
            rol=usuario.rol,
            activo=usuario.activo,
            creado_en=usuario.creado_en,
            actualizado_en=usuario.actualizado_en,
            ultimo_acceso=usuario.ultimo_acceso
        )
