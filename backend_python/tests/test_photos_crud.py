"""
Tests para los endpoints CRUD de fotos (requieren autenticación)
"""
import pytest
import io
from fastapi.testclient import TestClient
from typing import Dict, Any


# Marcador para tests que requieren base de datos
requires_db = pytest.mark.skip(reason="Base de datos no disponible - ejecutar con DB activa")


class TestCreatePhoto:
    """Tests para POST /api/photos"""

    def test_create_photo_without_auth(
        self, client: TestClient, sample_photo_data: Dict[str, Any]
    ):
        """Crear foto sin autenticación debe retornar 401"""
        # Crear imagen de prueba
        image_content = b"fake image content"
        files = {"image": ("test.jpg", io.BytesIO(image_content), "image/jpeg")}

        response = client.post(
            "/api/photos",
            data=sample_photo_data,
            files=files
        )

        assert response.status_code == 401

    @requires_db
    def test_create_photo_with_auth(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        sample_photo_data: Dict[str, Any]
    ):
        """Crear foto con autenticación debe ser exitoso"""
        # Crear imagen de prueba
        image_content = b"fake image content for testing"
        files = {"image": ("test.jpg", io.BytesIO(image_content), "image/jpeg")}

        response = client.post(
            "/api/photos",
            data=sample_photo_data,
            files=files,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == sample_photo_data["title"]
        assert data["lat"] == sample_photo_data["lat"]
        assert data["lng"] == sample_photo_data["lng"]
        assert "id" in data
        assert "image_url" in data
        assert "thumb_url" in data

    def test_create_photo_without_image(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        sample_photo_data: Dict[str, Any]
    ):
        """Crear foto sin imagen debe retornar error 422"""
        response = client.post(
            "/api/photos",
            data=sample_photo_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_create_photo_without_required_fields(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Crear foto sin campos requeridos debe retornar error"""
        image_content = b"fake image"
        files = {"image": ("test.jpg", io.BytesIO(image_content), "image/jpeg")}

        # Sin título
        response = client.post(
            "/api/photos",
            data={"lat": 41.65, "lng": -0.88},
            files=files,
            headers=auth_headers
        )

        assert response.status_code == 422

    @requires_db
    def test_create_photo_with_invalid_image_type(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        sample_photo_data: Dict[str, Any]
    ):
        """Crear foto con archivo no imagen debe retornar error"""
        files = {"image": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}

        response = client.post(
            "/api/photos",
            data=sample_photo_data,
            files=files,
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "imagen" in response.json()["detail"].lower()


@requires_db
class TestUpdatePhoto:
    """Tests para PUT /api/photos/{id}"""

    @pytest.fixture
    def created_photo_id(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ) -> int:
        """Fixture que crea una foto y retorna su ID"""
        image_content = b"test image for update"
        files = {"image": ("test.jpg", io.BytesIO(image_content), "image/jpeg")}
        data = {
            "title": "Foto para actualizar",
            "lat": 41.65,
            "lng": -0.88
        }

        response = client.post(
            "/api/photos",
            data=data,
            files=files,
            headers=auth_headers
        )
        return response.json()["id"]

    def test_update_photo_without_auth(
        self, client: TestClient, created_photo_id: int
    ):
        """Actualizar foto sin autenticación debe retornar 401"""
        response = client.put(
            f"/api/photos/{created_photo_id}",
            data={"title": "Nuevo titulo", "lat": 41.65, "lng": -0.88}
        )

        assert response.status_code == 401

    def test_update_photo_with_auth(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        created_photo_id: int
    ):
        """Actualizar foto con autenticación debe ser exitoso"""
        new_title = "Titulo actualizado"

        response = client.put(
            f"/api/photos/{created_photo_id}",
            data={
                "title": new_title,
                "lat": 41.66,
                "lng": -0.89,
                "description": "Nueva descripcion"
            },
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == new_title
        assert data["description"] == "Nueva descripcion"

    def test_update_photo_with_new_image(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        created_photo_id: int
    ):
        """Actualizar foto con nueva imagen debe ser exitoso"""
        new_image = b"new image content"
        files = {"image": ("new.jpg", io.BytesIO(new_image), "image/jpeg")}

        response = client.put(
            f"/api/photos/{created_photo_id}",
            data={"title": "Con nueva imagen", "lat": 41.65, "lng": -0.88},
            files=files,
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_update_nonexistent_photo(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Actualizar foto inexistente debe retornar 404"""
        response = client.put(
            "/api/photos/999999",
            data={"title": "No existe", "lat": 41.65, "lng": -0.88},
            headers=auth_headers
        )

        assert response.status_code == 404


@requires_db
class TestDeletePhoto:
    """Tests para DELETE /api/photos/{id}"""

    @pytest.fixture
    def photo_to_delete_id(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ) -> int:
        """Fixture que crea una foto para eliminar"""
        image_content = b"test image for delete"
        files = {"image": ("test.jpg", io.BytesIO(image_content), "image/jpeg")}
        data = {
            "title": "Foto para eliminar",
            "lat": 41.65,
            "lng": -0.88
        }

        response = client.post(
            "/api/photos",
            data=data,
            files=files,
            headers=auth_headers
        )
        return response.json()["id"]

    def test_delete_photo_without_auth(
        self, client: TestClient, photo_to_delete_id: int
    ):
        """Eliminar foto sin autenticación debe retornar 401"""
        response = client.delete(f"/api/photos/{photo_to_delete_id}")

        assert response.status_code == 401

    def test_delete_photo_with_auth(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        photo_to_delete_id: int
    ):
        """Eliminar foto con autenticación debe ser exitoso"""
        response = client.delete(
            f"/api/photos/{photo_to_delete_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # Verificar que la foto ya no existe
        get_response = client.get(f"/api/photos/{photo_to_delete_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_photo(
        self,
        client: TestClient,
        auth_headers: Dict[str, str]
    ):
        """Eliminar foto inexistente debe retornar 404"""
        response = client.delete(
            "/api/photos/999999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_delete_same_photo_twice(
        self,
        client: TestClient,
        auth_headers: Dict[str, str],
        photo_to_delete_id: int
    ):
        """Eliminar la misma foto dos veces debe retornar 404 la segunda vez"""
        # Primera eliminación
        response1 = client.delete(
            f"/api/photos/{photo_to_delete_id}",
            headers=auth_headers
        )
        assert response1.status_code == 200

        # Segunda eliminación
        response2 = client.delete(
            f"/api/photos/{photo_to_delete_id}",
            headers=auth_headers
        )
        assert response2.status_code == 404
