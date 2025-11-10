"""
Rutas de API para el módulo de Autenticación.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.models import Usuario, RolUsuario
from app.modules.auth.schemas import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    LoginRequest,
    TokenResponse,
    ChangePasswordRequest
)
from app.modules.auth.services import AuthService
from app.shared.dependencies import (
    get_current_active_user,
    require_admin
)


router = APIRouter(prefix="/auth")


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency para obtener el servicio de autenticación"""
    return AuthService(db)


@router.post(
    "/register",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description="Registra un nuevo usuario en el sistema"
)
async def register(
    usuario_data: UsuarioCreate,
    service: AuthService = Depends(get_auth_service)
):
    """
    Registra un nuevo usuario.

    Validaciones:
    - Username único
    - Email único
    - Contraseña mínimo 6 caracteres

    **Nota:** En producción, este endpoint debería estar protegido
    y solo admins deberían poder crear usuarios.
    """
    return service.register(usuario_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT"
)
async def login(
    login_data: LoginRequest,
    service: AuthService = Depends(get_auth_service)
):
    """
    Inicia sesión con username/email y contraseña.

    Retorna un token JWT que debe incluirse en las peticiones:
    ```
    Authorization: Bearer <token>
    ```

    El token expira según configuración (default: 30 minutos).
    """
    return service.login(login_data)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Obtener usuario actual",
    description="Obtiene los datos del usuario autenticado"
)
async def get_me(
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene los datos del usuario actual.

    Requiere autenticación (token JWT válido).
    """
    from app.modules.auth.services import AuthService
    service = AuthService(None)  # No necesita DB para esta conversión
    return service._to_response(current_user)


@router.put(
    "/me",
    response_model=UsuarioResponse,
    summary="Actualizar perfil",
    description="Actualiza los datos del usuario actual"
)
async def update_me(
    usuario_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_active_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Actualiza el perfil del usuario actual.

    No permite cambiar el rol (requiere permisos de admin).
    """
    # Prevenir que usuarios cambien su propio rol
    if usuario_data.rol is not None and usuario_data.rol != current_user.rol:
        if current_user.rol != RolUsuario.ADMIN:
            usuario_data.rol = current_user.rol  # Mantener rol actual

    return service.update_usuario(current_user.id, usuario_data)


@router.post(
    "/me/change-password",
    summary="Cambiar contraseña",
    description="Cambia la contraseña del usuario actual"
)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: Usuario = Depends(get_current_active_user),
    service: AuthService = Depends(get_auth_service)
):
    """
    Cambia la contraseña del usuario actual.

    Requiere:
    - Contraseña actual (para verificación)
    - Nueva contraseña (mínimo 6 caracteres)
    """
    return service.change_password(current_user.id, password_data)


# --- Endpoints de administración (requieren permisos) ---

@router.get(
    "/usuarios",
    response_model=dict,
    summary="Listar usuarios",
    description="Lista todos los usuarios (solo admin)"
)
async def list_usuarios(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    rol: Optional[RolUsuario] = Query(None),
    activo: Optional[bool] = Query(None),
    current_user: Usuario = Depends(require_admin),
    service: AuthService = Depends(get_auth_service)
):
    """
    Lista todos los usuarios del sistema.

    **Requiere:** Permisos de administrador

    Filtros opcionales:
    - **rol**: Filtrar por rol
    - **activo**: Filtrar por estado activo/inactivo
    """
    skip = (page - 1) * page_size
    usuarios, total = service.get_usuarios(
        skip=skip,
        limit=page_size,
        rol=rol,
        activo=activo
    )

    return {
        "total": total,
        "items": usuarios,
        "page": page,
        "page_size": page_size
    }


@router.get(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Obtener usuario por ID",
    description="Obtiene los datos de un usuario específico (solo admin)"
)
async def get_usuario(
    usuario_id: str,
    current_user: Usuario = Depends(require_admin),
    service: AuthService = Depends(get_auth_service)
):
    """
    Obtiene los datos de un usuario por su ID.

    **Requiere:** Permisos de administrador
    """
    return service.get_usuario_by_id(usuario_id)


@router.put(
    "/usuarios/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario",
    description="Actualiza un usuario (solo admin)"
)
async def update_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdate,
    current_user: Usuario = Depends(require_admin),
    service: AuthService = Depends(get_auth_service)
):
    """
    Actualiza los datos de un usuario.

    **Requiere:** Permisos de administrador
    """
    return service.update_usuario(usuario_id, usuario_data)


@router.delete(
    "/usuarios/{usuario_id}",
    summary="Eliminar usuario",
    description="Elimina un usuario (solo admin)"
)
async def delete_usuario(
    usuario_id: str,
    current_user: Usuario = Depends(require_admin),
    service: AuthService = Depends(get_auth_service)
):
    """
    Elimina un usuario del sistema.

    **Requiere:** Permisos de administrador

    **Nota:** No se puede eliminar a sí mismo.
    """
    if usuario_id == current_user.id:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )

    return service.delete_usuario(usuario_id)
