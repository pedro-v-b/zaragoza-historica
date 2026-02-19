"""
Servicio de lógica de negocio para fotos
"""
from typing import Dict
from models.schemas import PaginatedPhotos, FilterMetadata, Photo
from repositories.photos_repository import photos_repository
import math


class PhotosService:
    """Servicio de fotos con lógica de negocio"""
    
    def get_photos(self, filters: dict) -> PaginatedPhotos:
        """Obtiene fotos con filtros y paginación"""
        photos_data, total = photos_repository.find_all(filters)
        
        page = filters.get('page', 1)
        page_size = filters.get('pageSize', 20)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        
        # Convertir a modelos Pydantic
        photos = [Photo(**photo) for photo in photos_data]
        
        return PaginatedPhotos(
            items=photos,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    def get_photo_by_id(self, photo_id: int) -> Photo:
        """Obtiene una foto por ID"""
        photo_data = photos_repository.find_by_id(photo_id)
        
        if not photo_data:
            return None
        
        return Photo(**photo_data)
    
    def get_filter_metadata(self) -> FilterMetadata:
        """Obtiene metadatos para filtros dinámicos"""
        eras = photos_repository.get_distinct_eras()
        zones = photos_repository.get_distinct_zones()
        year_range = photos_repository.get_year_range()
        
        return FilterMetadata(
            eras=eras,
            zones=zones,
            yearRange=year_range
        )


# Singleton
photos_service = PhotosService()
