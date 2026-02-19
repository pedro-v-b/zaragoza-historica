"""
Configuración y fixtures para pytest
"""
import os
import sys
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient

# Añadir el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from services.auth_service import auth_service
from config.auth import auth_config


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Cliente de pruebas para la API"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def admin_credentials() -> Dict[str, str]:
    """Credenciales del usuario admin"""
    return {
        "username": auth_config.ADMIN_USERNAME,
        "password": auth_config.ADMIN_PASSWORD
    }


@pytest.fixture(scope="module")
def admin_token(client: TestClient, admin_credentials: Dict[str, str]) -> str:
    """Token JWT válido para el usuario admin"""
    response = client.post("/api/auth/login", json=admin_credentials)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(admin_token: str) -> Dict[str, str]:
    """Headers de autorización con token JWT"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def invalid_token() -> str:
    """Token JWT inválido para pruebas de autenticación fallida"""
    return "invalid.token.here"


@pytest.fixture
def invalid_auth_headers(invalid_token: str) -> Dict[str, str]:
    """Headers con token inválido"""
    return {"Authorization": f"Bearer {invalid_token}"}


@pytest.fixture
def sample_photo_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear una foto"""
    return {
        "title": "Foto de prueba",
        "description": "Descripcion de la foto de prueba",
        "year": 1950,
        "era": "Anos 50",
        "zone": "Centro",
        "lat": 41.6488,
        "lng": -0.8891,
        "source": "Test Source",
        "author": "Test Author",
        "rights": "Dominio publico",
    }


@pytest.fixture
def sample_photo_data_minimal() -> Dict[str, Any]:
    """Datos mínimos para crear una foto"""
    return {
        "title": "Foto minima",
        "lat": 41.65,
        "lng": -0.88,
    }


# Configuración de pytest-asyncio
@pytest.fixture(scope="session")
def event_loop_policy():
    """Política de event loop para tests async"""
    import asyncio
    return asyncio.DefaultEventLoopPolicy()
