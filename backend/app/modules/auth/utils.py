"""
Utilidades para autenticación: JWT, password hashing, etc.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt

from app.config import settings


def hash_password(password: str) -> str:
    """
    Hashea una contraseña usando bcrypt.

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Password hasheada
    """
    # Truncar password a 72 bytes (límite de bcrypt)
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña

    Returns:
        bool: True si coincide, False si no
    """
    # Truncar password a 72 bytes (límite de bcrypt)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso.

    Args:
        data: Datos a incluir en el token (típicamente user_id, username, etc.)
        expires_delta: Tiempo de expiración custom (opcional)

    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()

    # Calcular expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Crear token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodifica un token JWT.

    Args:
        token: Token JWT

    Returns:
        dict: Payload del token, o None si es inválido
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def validate_token(token: str) -> tuple[bool, Optional[str], Optional[dict]]:
    """
    Valida un token JWT y extrae su payload.

    Args:
        token: Token JWT

    Returns:
        tuple: (es_valido, mensaje_error, payload)
    """
    if not token:
        return False, "Token no proporcionado", None

    payload = decode_access_token(token)

    if payload is None:
        return False, "Token inválido o expirado", None

    # Verificar que tenga los campos requeridos
    user_id = payload.get("sub")
    if not user_id:
        return False, "Token malformado", None

    return True, None, payload
