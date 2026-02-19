"""
Tests para el endpoint de health check
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Tests para /api/health"""

    def test_health_check_returns_ok(self, client: TestClient):
        """El health check debe retornar status ok"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_health_check_has_valid_timestamp(self, client: TestClient):
        """El health check debe incluir un timestamp válido"""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        # El timestamp debe ser un string ISO format
        assert isinstance(data["timestamp"], str)
        assert "T" in data["timestamp"]  # ISO format tiene T separando fecha y hora
