"""
Repository para autenticación
En esta versión usa usuario hardcodeado desde variables de entorno
"""
from typing import Optional
import bcrypt
from config.auth import auth_config


class AuthRepository:
    """Repository para acceso a datos de autenticación"""

    def __init__(self):
        # Hash de la contraseña del admin al inicializar
        self._admin_password_hash = self.hash_password(auth_config.ADMIN_PASSWORD)

    def find_user_by_username(self, username: str) -> Optional[dict]:
        """
        Busca un usuario por username
        En esta versión solo existe el usuario admin hardcodeado
        """
        if username == auth_config.ADMIN_USERNAME:
            return {
                "id": 1,
                "username": auth_config.ADMIN_USERNAME,
                "password_hash": self._admin_password_hash,
                "role": "admin",
                "is_active": True
            }
        return None

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def hash_password(self, password: str) -> str:
        """Genera hash de una contraseña"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')


# Singleton
auth_repository = AuthRepository()
