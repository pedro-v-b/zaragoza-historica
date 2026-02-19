"""
Router para endpoints de fotos
"""
import os
import uuid
import json
import shutil
from fastapi import APIRouter, HTTPException, Query, Depends, File, UploadFile, Form
from typing import Optional, List
from models.schemas import PaginatedPhotos, FilterMetadata, Photo, TokenData, MessageResponse
from services.photos_service import photos_service
from dependencies.auth import get_current_user

router = APIRouter(prefix="/photos", tags=["photos"])

# Directorio de uploads
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
THUMBS_DIR = os.path.join(UPLOADS_DIR, "thumbs")


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


def save_uploaded_image(file: UploadFile) -> tuple[str, str]:
    """Guarda una imagen y genera thumbnail. Retorna (image_url, thumb_url)"""
    # Crear directorios si no existen
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(THUMBS_DIR, exist_ok=True)

    # Generar nombre único
    ext = os.path.splitext(file.filename)[1] or '.jpg'
    filename = f"{uuid.uuid4()}{ext}"

    # Guardar imagen original
    image_path = os.path.join(UPLOADS_DIR, filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Para simplificar, usamos la misma imagen como thumbnail
    # En producción se generaría un thumbnail real con Pillow
    thumb_path = os.path.join(THUMBS_DIR, filename)
    shutil.copy(image_path, thumb_path)

    return f"/uploads/{filename}", f"/uploads/thumbs/{filename}"


@router.post("", response_model=Photo)
async def create_photo(
    title: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    image: UploadFile = File(...),
    description: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    year_from: Optional[int] = Form(None),
    year_to: Optional[int] = Form(None),
    era: Optional[str] = Form(None),
    zone: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    rights: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Crea una nueva foto (requiere autenticacion)
    """
    # Validar que sea una imagen
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")

    # Guardar imagen
    image_url, thumb_url = save_uploaded_image(image)

    # Parsear tags si vienen como JSON
    tags_list = None
    if tags:
        try:
            tags_list = json.loads(tags)
        except json.JSONDecodeError:
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]

    data = {
        'title': title,
        'description': description,
        'year': year,
        'year_from': year_from,
        'year_to': year_to,
        'era': era,
        'zone': zone,
        'lat': lat,
        'lng': lng,
        'image_url': image_url,
        'thumb_url': thumb_url,
        'source': source,
        'author': author,
        'rights': rights,
        'tags': tags_list,
    }

    return photos_service.create_photo(data)


@router.put("/{photo_id}", response_model=Photo)
async def update_photo(
    photo_id: int,
    title: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    image: Optional[UploadFile] = File(None),
    description: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    year_from: Optional[int] = Form(None),
    year_to: Optional[int] = Form(None),
    era: Optional[str] = Form(None),
    zone: Optional[str] = Form(None),
    source: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    rights: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Actualiza una foto existente (requiere autenticacion)
    """
    # Verificar que la foto existe
    existing = photos_service.get_photo_by_id(photo_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Foto con ID {photo_id} no encontrada")

    # Parsear tags
    tags_list = None
    if tags:
        try:
            tags_list = json.loads(tags)
        except json.JSONDecodeError:
            tags_list = [t.strip() for t in tags.split(',') if t.strip()]

    data = {
        'title': title,
        'description': description,
        'year': year,
        'year_from': year_from,
        'year_to': year_to,
        'era': era,
        'zone': zone,
        'lat': lat,
        'lng': lng,
        'source': source,
        'author': author,
        'rights': rights,
        'tags': tags_list,
    }

    # Si hay nueva imagen, guardarla
    if image and image.filename:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="El archivo debe ser una imagen")
        image_url, thumb_url = save_uploaded_image(image)
        data['image_url'] = image_url
        data['thumb_url'] = thumb_url

    photo = photos_service.update_photo(photo_id, data)

    if not photo:
        raise HTTPException(status_code=404, detail=f"Foto con ID {photo_id} no encontrada")

    return photo


@router.delete("/{photo_id}", response_model=MessageResponse)
async def delete_photo(
    photo_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Elimina una foto (requiere autenticacion)
    """
    # Verificar que la foto existe
    existing = photos_service.get_photo_by_id(photo_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Foto con ID {photo_id} no encontrada")

    success = photos_service.delete_photo(photo_id)

    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar la foto")

    return MessageResponse(message=f"Foto {photo_id} eliminada correctamente", success=True)
