"""
Router para endpoints de fotos
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import PaginatedPhotos, FilterMetadata, Photo
from services.photos_service import photos_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/metadata/filters", response_model=FilterMetadata)
async def get_filter_metadata():
    """Obtiene metadatos para los filtros (épocas, zonas, rango de años)"""
    return photos_service.get_filter_metadata()


@router.get("/{photo_id}", response_model=Photo)
async def get_photo_by_id(photo_id: int):
    """Obtiene una foto específica por ID"""
    photo = photos_service.get_photo_by_id(photo_id)
    
    if not photo:
        raise HTTPException(status_code=404, detail=f"Foto con ID {photo_id} no encontrada")
    
    return photo


@router.get("", response_model=PaginatedPhotos)
async def get_photos(
    bbox: Optional[str] = Query(None, description="Bounding box: 'minLng,minLat,maxLng,maxLat'"),
    yearFrom: Optional[int] = Query(None, description="Año desde"),
    yearTo: Optional[int] = Query(None, description="Año hasta"),
    era: Optional[str] = Query(None, description="Época histórica"),
    zone: Optional[str] = Query(None, description="Zona de Zaragoza"),
    q: Optional[str] = Query(None, description="Búsqueda de texto"),
    page: int = Query(1, ge=1, description="Número de página"),
    pageSize: int = Query(20, ge=1, le=100, description="Resultados por página")
):
    """
    Obtiene fotos con filtros combinables y paginación
    
    Filtros disponibles:
    - **bbox**: Bounding box geográfico (minLng,minLat,maxLng,maxLat)
    - **yearFrom**, **yearTo**: Rango de años
    - **era**: Época histórica específica
    - **zone**: Zona de Zaragoza
    - **q**: Búsqueda en título, descripción y tags
    """
    filters = {
        'bbox': bbox,
        'yearFrom': yearFrom,
        'yearTo': yearTo,
        'era': era,
        'zone': zone,
        'q': q,
        'page': page,
        'pageSize': pageSize
    }
    
    return photos_service.get_photos(filters)
