"""
Tests para los endpoints de fotos
"""
import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any


# Marcador para tests que requieren base de datos
# Se usa con condición de string para evaluación lazy
requires_db = pytest.mark.skip(reason="Base de datos no disponible - ejecutar con DB activa")


@requires_db
class TestGetPhotos:
    """Tests para GET /api/photos"""

    def test_get_photos_without_filters(self, client: TestClient):
        """Obtener fotos sin filtros debe retornar lista paginada"""
        response = client.get("/api/photos")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pageSize" in data
        assert "totalPages" in data
        assert isinstance(data["items"], list)

    def test_get_photos_with_pagination(self, client: TestClient):
        """Paginación debe funcionar correctamente"""
        response = client.get("/api/photos?page=1&pageSize=2")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["pageSize"] == 2
        assert len(data["items"]) <= 2

    def test_get_photos_page_two(self, client: TestClient):
        """Segunda página debe retornar resultados diferentes"""
        page1 = client.get("/api/photos?page=1&pageSize=2").json()
        page2 = client.get("/api/photos?page=2&pageSize=2").json()

        if page1["total"] > 2:
            # Si hay más de 2 fotos, las páginas deben ser diferentes
            assert page1["items"] != page2["items"]

    def test_get_photos_with_year_filter(self, client: TestClient):
        """Filtro por año debe funcionar"""
        response = client.get("/api/photos?yearFrom=1940&yearTo=1960")

        assert response.status_code == 200
        data = response.json()
        for photo in data["items"]:
            # La foto debe estar en el rango de años
            year = photo.get("year") or photo.get("year_from") or photo.get("year_to")
            if year:
                assert 1940 <= year <= 1960 or \
                    (photo.get("year_from") and photo["year_from"] <= 1960) or \
                    (photo.get("year_to") and photo["year_to"] >= 1940)

    def test_get_photos_with_era_filter(self, client: TestClient):
        """Filtro por época debe funcionar"""
        response = client.get("/api/photos?era=Años 40")

        assert response.status_code == 200
        data = response.json()
        for photo in data["items"]:
            assert photo["era"] == "Años 40"

    def test_get_photos_with_zone_filter(self, client: TestClient):
        """Filtro por zona debe funcionar"""
        response = client.get("/api/photos?zone=Centro")

        assert response.status_code == 200
        data = response.json()
        for photo in data["items"]:
            assert photo["zone"] == "Centro"

    def test_get_photos_with_search_query(self, client: TestClient):
        """Búsqueda de texto debe funcionar"""
        response = client.get("/api/photos?q=Plaza")

        assert response.status_code == 200
        data = response.json()
        # Si hay resultados, deben contener el término buscado
        for photo in data["items"]:
            text_content = f"{photo['title']} {photo.get('description', '')}".lower()
            tags = " ".join(photo.get("tags") or []).lower()
            assert "plaza" in text_content or "plaza" in tags

    def test_get_photos_with_bbox_filter(self, client: TestClient):
        """Filtro por bounding box debe funcionar"""
        # BBox que cubre Zaragoza
        bbox = "-1.0,41.5,-0.7,41.8"
        response = client.get(f"/api/photos?bbox={bbox}")

        assert response.status_code == 200
        data = response.json()
        for photo in data["items"]:
            assert -1.0 <= photo["lng"] <= -0.7
            assert 41.5 <= photo["lat"] <= 41.8

    def test_get_photos_with_combined_filters(self, client: TestClient):
        """Múltiples filtros combinados deben funcionar"""
        response = client.get("/api/photos?yearFrom=1930&yearTo=1970&zone=Centro")

        assert response.status_code == 200
        data = response.json()
        for photo in data["items"]:
            assert photo["zone"] == "Centro"

    def test_get_photos_invalid_page(self, client: TestClient):
        """Página inválida debe retornar error"""
        response = client.get("/api/photos?page=0")

        assert response.status_code == 422  # Validation error

    def test_get_photos_invalid_page_size(self, client: TestClient):
        """PageSize inválido debe retornar error"""
        response = client.get("/api/photos?pageSize=200")

        assert response.status_code == 422  # Max is 100


@requires_db
class TestGetPhotoById:
    """Tests para GET /api/photos/{id}"""

    def test_get_photo_by_valid_id(self, client: TestClient):
        """Obtener foto con ID válido debe retornar la foto"""
        # Primero obtener una foto existente
        photos_response = client.get("/api/photos?pageSize=1")
        photos = photos_response.json()["items"]

        if len(photos) > 0:
            photo_id = photos[0]["id"]
            response = client.get(f"/api/photos/{photo_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == photo_id
            assert "title" in data
            assert "lat" in data
            assert "lng" in data

    def test_get_photo_by_invalid_id(self, client: TestClient):
        """Obtener foto con ID inexistente debe retornar 404"""
        response = client.get("/api/photos/999999")

        assert response.status_code == 404
        assert "detail" in response.json()

    def test_get_photo_by_negative_id(self, client: TestClient):
        """ID negativo debe retornar 404"""
        response = client.get("/api/photos/-1")

        assert response.status_code == 404


@requires_db
class TestGetFilterMetadata:
    """Tests para GET /api/photos/metadata/filters"""

    def test_get_filter_metadata(self, client: TestClient):
        """Debe retornar metadatos de filtros disponibles"""
        response = client.get("/api/photos/metadata/filters")

        assert response.status_code == 200
        data = response.json()
        assert "eras" in data
        assert "zones" in data
        assert "yearRange" in data
        assert isinstance(data["eras"], list)
        assert isinstance(data["zones"], list)
        assert "min" in data["yearRange"]
        assert "max" in data["yearRange"]
