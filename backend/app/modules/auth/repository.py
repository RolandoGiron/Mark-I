"""
Repositorio para acceso a datos del módulo de Autenticación.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.modules.auth.models import Usuario, RolUsuario
from app.modules.auth.schemas import UsuarioCreate, UsuarioUpdate


class UsuarioRepository:
    """Repositorio para operaciones CRUD de Usuarios"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, usuario_id: str) -> Optional[Usuario]:
        """Obtiene un usuario por su ID"""
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def get_by_username(self, username: str) -> Optional[Usuario]:
        """Obtiene un usuario por su username"""
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def get_by_email(self, email: str) -> Optional[Usuario]:
        """Obtiene un usuario por su email"""
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def get_by_telegram_id(self, telegram_id: str) -> Optional[Usuario]:
        """Obtiene un usuario por su Telegram ID"""
        return self.db.query(Usuario).filter(Usuario.telegram_id == telegram_id).first()

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        rol: Optional[RolUsuario] = None,
        activo: Optional[bool] = None
    ) -> tuple[List[Usuario], int]:
        """Obtiene lista de usuarios con filtros"""
        query = self.db.query(Usuario)

        if rol:
            query = query.filter(Usuario.rol == rol)

        if activo is not None:
            query = query.filter(Usuario.activo == activo)

        total = query.count()
        usuarios = query.order_by(Usuario.nombre_completo).offset(skip).limit(limit).all()

        return usuarios, total

    def create(self, usuario_data: UsuarioCreate, hashed_password: str) -> Usuario:
        """Crea un nuevo usuario"""
        usuario = Usuario(
            **usuario_data.model_dump(exclude={"password"}),
            hashed_password=hashed_password
        )
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update(self, usuario: Usuario, usuario_data: UsuarioUpdate) -> Usuario:
        """Actualiza un usuario existente"""
        update_data = usuario_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(usuario, field, value)

        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update_password(self, usuario: Usuario, hashed_password: str) -> Usuario:
        """Actualiza la contraseña de un usuario"""
        usuario.hashed_password = hashed_password
        self.db.commit()
        self.db.refresh(usuario)
        return usuario

    def update_ultimo_acceso(self, usuario: Usuario) -> Usuario:
        """Actualiza la fecha de último acceso"""
        from datetime import datetime
        usuario.ultimo_acceso = datetime.utcnow()
        self.db.commit()
        return usuario

    def delete(self, usuario: Usuario) -> bool:
        """Elimina un usuario"""
        self.db.delete(usuario)
        self.db.commit()
        return True

    def exists_username(self, username: str, exclude_id: Optional[str] = None) -> bool:
        """Verifica si existe un username"""
        query = self.db.query(Usuario).filter(Usuario.username == username)

        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)

        return query.first() is not None

    def exists_email(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """Verifica si existe un email"""
        query = self.db.query(Usuario).filter(Usuario.email == email)

        if exclude_id:
            query = query.filter(Usuario.id != exclude_id)

        return query.first() is not None
