"""
Servicio de lógica de negocio para fotos
"""
import math
import time
from typing import Dict, Optional, Tuple

from models.schemas import PaginatedPhotos, FilterMetadata, Photo
from repositories.photos_repository import photos_repository


# TTL del caché de metadatos de filtros (épocas, zonas, años)
_FILTER_METADATA_TTL = 300  # 5 min


class PhotosService:
    """Servicio de fotos con lógica de negocio"""

    def __init__(self) -> None:
        self._filter_cache: Optional[Tuple[float, FilterMetadata]] = None

    def get_photos(self, filters: dict) -> PaginatedPhotos:
        """Obtiene fotos con filtros y paginación"""
        photos_data, total = photos_repository.find_all(filters)

        page = filters.get('page', 1)
        page_size = filters.get('pageSize', 20)
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        photos = [Photo(**photo) for photo in photos_data]

        return PaginatedPhotos(
            items=photos,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages,
        )

    def get_photos_raw(self, filters: dict):
        """Obtiene fotos sin convertir a modelos Pydantic para mayor velocidad"""
        return photos_repository.find_all(filters)

    def get_map_points(self, filters: dict, limit: int):
        """Proyección ligera para el mapa."""
        return photos_repository.find_map_points(filters, limit)

    def get_photo_by_id(self, photo_id: int) -> Optional[Photo]:
        photo_data = photos_repository.find_by_id(photo_id)
        if not photo_data:
            return None
        return Photo(**photo_data)

    def get_filter_metadata(self) -> FilterMetadata:
        """Metadatos para filtros dinámicos. Cacheados en memoria (TTL)."""
        now = time.time()
        if self._filter_cache and now - self._filter_cache[0] < _FILTER_METADATA_TTL:
            return self._filter_cache[1]

        data = photos_repository.get_filter_metadata()
        metadata = FilterMetadata(
            eras=data['eras'],
            zones=data['zones'],
            yearRange=data['yearRange'],
        )
        self._filter_cache = (now, metadata)
        return metadata

    def invalidate_filter_metadata(self) -> None:
        """Invalida el caché tras un create/update/delete."""
        self._filter_cache = None

    def create_photo(self, data: dict) -> Photo:
        photo_data = photos_repository.create(data)
        self.invalidate_filter_metadata()
        return Photo(**photo_data)

    def update_photo(self, photo_id: int, data: dict) -> Optional[Photo]:
        photo_data = photos_repository.update(photo_id, data)
        if not photo_data:
            return None
        self.invalidate_filter_metadata()
        return Photo(**photo_data)

    def delete_photo(self, photo_id: int) -> bool:
        deleted = photos_repository.delete(photo_id)
        if deleted:
            self.invalidate_filter_metadata()
        return deleted


# Singleton
photos_service = PhotosService()
