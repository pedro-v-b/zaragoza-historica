"""
Configuración de autenticación JWT
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class AuthConfig:
    """Configuración de autenticación"""

    # JWT Settings
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    # Admin user (hardcoded from env)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    @classmethod
    def get_token_expiry(cls) -> timedelta:
        """Obtiene la duración del token"""
        return timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)


auth_config = AuthConfig()
