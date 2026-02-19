"""
Tests para los endpoints de autenticación
"""
import pytest
from fastapi.testclient import TestClient
from typing import Dict


class TestLogin:
    """Tests para POST /api/auth/login"""

    def test_login_with_valid_credentials(
        self, client: TestClient, admin_credentials: Dict[str, str]
    ):
        """Login con credenciales válidas debe retornar token"""
        response = client.post("/api/auth/login", json=admin_credentials)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == admin_credentials["username"]
        assert data["user"]["role"] == "admin"

    def test_login_with_invalid_username(self, client: TestClient):
        """Login con usuario inválido debe retornar 401"""
        response = client.post("/api/auth/login", json={
            "username": "usuario_inexistente",
            "password": "password123"
        })

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_with_invalid_password(
        self, client: TestClient, admin_credentials: Dict[str, str]
    ):
        """Login con contraseña inválida debe retornar 401"""
        response = client.post("/api/auth/login", json={
            "username": admin_credentials["username"],
            "password": "wrong_password"
        })

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_with_empty_credentials(self, client: TestClient):
        """Login con credenciales vacías debe retornar 422"""
        response = client.post("/api/auth/login", json={
            "username": "",
            "password": ""
        })

        # FastAPI retorna 422 para validación fallida
        assert response.status_code == 422

    def test_login_without_body(self, client: TestClient):
        """Login sin body debe retornar 422"""
        response = client.post("/api/auth/login")

        assert response.status_code == 422


class TestLogout:
    """Tests para POST /api/auth/logout"""

    def test_logout_with_valid_token(
        self, client: TestClient, admin_credentials: Dict[str, str]
    ):
        """Logout con token válido debe ser exitoso"""
        # Crear un token fresco solo para este test (no usar el compartido)
        login_response = client.post("/api/auth/login", json=admin_credentials)
        fresh_token = login_response.json()["access_token"]
        fresh_headers = {"Authorization": f"Bearer {fresh_token}"}

        response = client.post("/api/auth/logout", headers=fresh_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

    def test_logout_without_token(self, client: TestClient):
        """Logout sin token debe retornar 401"""
        response = client.post("/api/auth/logout")

        assert response.status_code == 401

    def test_logout_with_invalid_token(
        self, client: TestClient, invalid_auth_headers: Dict[str, str]
    ):
        """Logout con token inválido debe retornar 401"""
        response = client.post("/api/auth/logout", headers=invalid_auth_headers)

        assert response.status_code == 401


class TestMe:
    """Tests para GET /api/auth/me"""

    def test_me_with_valid_token(
        self, client: TestClient, admin_credentials: Dict[str, str]
    ):
        """GET /me con token válido debe retornar datos del usuario"""
        # Primero hacer login para obtener token fresco
        login_response = client.post("/api/auth/login", json=admin_credentials)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == admin_credentials["username"]
        assert data["role"] == "admin"
        assert data["is_active"] is True

    def test_me_without_token(self, client: TestClient):
        """GET /me sin token debe retornar 401"""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_me_with_invalid_token(
        self, client: TestClient, invalid_auth_headers: Dict[str, str]
    ):
        """GET /me con token inválido debe retornar 401"""
        response = client.get("/api/auth/me", headers=invalid_auth_headers)

        assert response.status_code == 401
