"""
Configuración de autenticación JWT
"""
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


_INSECURE_DEFAULTS = {
    "",
    "dev-secret-key-change-in-production",
    "changeme",
    "secret",
}


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value or value in _INSECURE_DEFAULTS:
        sys.stderr.write(
            f"\n[FATAL] La variable de entorno {name} no esta configurada "
            f"o usa un valor inseguro por defecto.\n"
            f"        Genera una clave con: python -c \"import secrets; print(secrets.token_urlsafe(64))\"\n"
            f"        y anadela al fichero .env\n\n"
        )
        raise RuntimeError(f"{name} no configurada")
    return value


class AuthConfig:
    """Configuración de autenticación"""

    SECRET_KEY: str = _require_env("JWT_SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = _require_env("ADMIN_PASSWORD")

    @classmethod
    def get_token_expiry(cls) -> timedelta:
        return timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)


auth_config = AuthConfig()
