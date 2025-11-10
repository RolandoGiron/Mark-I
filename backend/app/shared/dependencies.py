"""
Dependencies compartidas para FastAPI.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.modules.auth.models import Usuario, RolUsuario
from app.modules.auth.services import AuthService
from app.modules.auth.utils import validate_token


# Security scheme para JWT
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependency para obtener el usuario actual desde el token JWT.

    Uso:
        @app.get("/protected")
        def protected_route(current_user: Usuario = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    token = credentials.credentials

    # Validar token
    is_valid, error, payload = validate_token(token)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Token inválido",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Obtener usuario
    user_id = payload.get("sub")
    auth_service = AuthService(db)

    try:
        usuario = auth_service.get_current_user(user_id)
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo autenticar el usuario",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Dependency para verificar que el usuario esté activo.
    """
    if not current_user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user


def require_admin(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency para requerir rol de administrador.

    Uso:
        @app.post("/admin/action")
        def admin_action(current_user: Usuario = Depends(require_admin)):
            # Solo admins pueden acceder
            return {"message": "Admin action"}
    """
    if current_user.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


def require_gerente_or_admin(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency para requerir rol de gerente o administrador.
    """
    if current_user.rol not in [RolUsuario.ADMIN, RolUsuario.GERENTE]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de gerente o administrador"
        )
    return current_user


def can_validate_expenses(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency para verificar permisos de validación de gastos.
    """
    if not current_user.puede_validar_gastos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para validar gastos"
        )
    return current_user


# Dependency opcional para rutas que pueden funcionar con o sin autenticación
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[Usuario]:
    """
    Dependency para obtener el usuario actual si está autenticado, None si no.

    Uso:
        @app.get("/public-or-private")
        def route(current_user: Optional[Usuario] = Depends(get_current_user_optional)):
            if current_user:
                return {"message": f"Hello {current_user.username}"}
            return {"message": "Hello guest"}
    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
