"""
Tests para los endpoints de capas del mapa
"""
import pytest
from fastapi.testclient import TestClient


# Marcador para tests que requieren base de datos
requires_db = pytest.mark.skip(reason="Base de datos no disponible - ejecutar con DB activa")


@requires_db
class TestGetLayers:
    """Tests para GET /api/layers"""

    def test_get_layers_returns_list(self, client: TestClient):
        """Obtener capas debe retornar una lista"""
        response = client.get("/api/layers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_layers_structure(self, client: TestClient):
        """Las capas deben tener la estructura correcta"""
        response = client.get("/api/layers")

        assert response.status_code == 200
        data = response.json()

        if len(data) > 0:
            layer = data[0]
            assert "id" in layer
            assert "name" in layer
            assert "type" in layer
            assert "min_zoom" in layer
            assert "max_zoom" in layer
            assert "is_active" in layer

    def test_get_layers_only_active(self, client: TestClient):
        """Solo deben retornarse capas activas"""
        response = client.get("/api/layers")

        assert response.status_code == 200
        data = response.json()

        for layer in data:
            assert layer["is_active"] is True


@requires_db
class TestGetLayerById:
    """Tests para GET /api/layers/{id}"""

    def test_get_layer_by_valid_id(self, client: TestClient):
        """Obtener capa con ID válido debe retornar la capa"""
        # Primero obtener una capa existente
        layers_response = client.get("/api/layers")
        layers = layers_response.json()

        if len(layers) > 0:
            layer_id = layers[0]["id"]
            response = client.get(f"/api/layers/{layer_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == layer_id

    def test_get_layer_by_invalid_id(self, client: TestClient):
        """Obtener capa con ID inexistente debe retornar 404"""
        response = client.get("/api/layers/999999")

        assert response.status_code == 404
        assert "detail" in response.json()
