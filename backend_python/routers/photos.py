"""
Router para endpoints de fotos
"""
import os
import io
import uuid
import json
import logging
from PIL import Image, UnidentifiedImageError
from fastapi import APIRouter, HTTPException, Query, Depends, File, UploadFile, Form, Request
from typing import Optional, List
from models.schemas import PaginatedPhotos, FilterMetadata, Photo, TokenData, MessageResponse, MapPhoto
from services.photos_service import photos_service
from dependencies.auth import get_current_user
from config.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/photos", tags=["photos"])

# Limites de upload
MAX_UPLOAD_BYTES = 15 * 1024 * 1024           # 15 MB
MAX_DIMENSION = 6000                           # 6000 px lado maximo
THUMB_SIZE = (400, 400)                        # miniatura 400x400 max
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

# Directorio de uploads
def get_uploads_dir():
    env_path = os.environ.get('UPLOADS_DIR')
    if env_path:
        return os.path.abspath(env_path)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))

UPLOADS_DIR = get_uploads_dir()
THUMBS_DIR = os.path.join(UPLOADS_DIR, "thumbs")


@router.get("/metadata/filters", response_model=FilterMetadata)
async def get_filter_metadata():
    """Obtiene metadatos para los filtros (épocas, zonas, rango de años)"""
    return photos_service.get_filter_metadata()


@router.get("/{photo_id:int}", response_model=Photo)
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
    pageSize: int = Query(20, ge=1, le=10000, description="Resultados por página"),
    randomOrder: bool = Query(False, description="Ordena los resultados aleatoriamente"),
    seed: Optional[float] = Query(None, ge=-1.0, le=1.0, description="Semilla para el orden aleatorio (paginacion estable)")
):
    """Obtiene fotos con filtros y paginación"""
    filters = {
        'bbox': bbox,
        'yearFrom': yearFrom,
        'yearTo': yearTo,
        'era': era,
        'zone': zone,
        'q': q,
        'page': page,
        'pageSize': pageSize,
        'randomOrder': randomOrder,
        'seed': seed,
    }

    return photos_service.get_photos(filters)


def save_uploaded_image(file: UploadFile) -> tuple[str, str]:
    """
    Valida, guarda una imagen y genera un thumbnail real redimensionado.
    Limpia archivos huerfanos si falla en cualquier paso.
    Lanza HTTPException si la imagen no es valida o supera los limites.
    """
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(THUMBS_DIR, exist_ok=True)

    # Leer todo el contenido a memoria con limite
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"La imagen supera el tamano maximo ({MAX_UPLOAD_BYTES // (1024 * 1024)} MB)"
        )
    if not data:
        raise HTTPException(status_code=400, detail="Archivo vacio")

    # Validar que es una imagen real (no solo el content-type)
    try:
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()
    except (UnidentifiedImageError, Exception) as exc:
        logger.warning("Upload rechazado: no es una imagen valida (%s)", exc)
        raise HTTPException(status_code=400, detail="El archivo no es una imagen valida")

    # Reabrir (verify cierra el puntero) y comprobar formato + dimensiones
    try:
        im = Image.open(io.BytesIO(data))
        fmt = (im.format or "").upper()
        if fmt not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato {fmt or 'desconocido'} no permitido. Usa JPEG, PNG o WebP."
            )
        if im.width > MAX_DIMENSION or im.height > MAX_DIMENSION:
            raise HTTPException(
                status_code=400,
                detail=f"Las dimensiones superan el maximo ({MAX_DIMENSION}px)"
            )
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGB")
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Upload rechazado: error procesando imagen (%s)", exc)
        raise HTTPException(status_code=400, detail="No se pudo procesar la imagen")

    # Extension original mapeada a formato real (ignora la del filename del cliente)
    ext_map = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
    ext = ext_map.get(fmt, ".jpg")
    filename = f"{uuid.uuid4()}{ext}"
    image_path = os.path.join(UPLOADS_DIR, filename)
    thumb_path = os.path.join(THUMBS_DIR, filename)

    try:
        # Guardar original
        with open(image_path, "wb") as f:
            f.write(data)

        # Generar miniatura real (aspect-ratio-preserving)
        thumb = im.copy()
        thumb.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
        if fmt == "PNG":
            thumb.save(thumb_path, "PNG", optimize=True)
        elif fmt == "WEBP":
            thumb.save(thumb_path, "WEBP", quality=85, method=4)
        else:
            thumb.save(thumb_path, "JPEG", quality=85, optimize=True, progressive=True)
    except Exception as exc:
        # Limpieza ante fallo parcial
        for p in (image_path, thumb_path):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except OSError:
                pass
        logger.exception("Error guardando imagen subida")
        raise HTTPException(status_code=500, detail="No se pudo guardar la imagen") from exc
    finally:
        try:
            im.close()
        except Exception:
            pass

    return f"/uploads/{filename}", f"/uploads/thumbs/{filename}"


@router.post("", response_model=Photo)
@limiter.limit("20/minute")
async def create_photo(
    request: Request,
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
    image_url, thumb_url = save_uploaded_image(image)
    tags_list = None
    if tags:
        try: tags_list = json.loads(tags)
        except: tags_list = [t.strip() for t in tags.split(',') if t.strip()]
    data = {
        'title': title, 'description': description, 'year': year,
        'year_from': year_from, 'year_to': year_to, 'era': era, 'zone': zone,
        'lat': lat, 'lng': lng, 'image_url': image_url, 'thumb_url': thumb_url,
        'source': source, 'author': author, 'rights': rights, 'tags': tags_list,
    }
    try:
        return photos_service.create_photo(data)
    except Exception:
        # Limpiar archivos huerfanos si falla la insercion en BD
        _cleanup_upload(image_url, thumb_url)
        logger.exception("Error creando foto en BD, archivos eliminados")
        raise


@router.put("/{photo_id:int}", response_model=Photo)
@limiter.limit("20/minute")
async def update_photo(
    request: Request,
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
    existing = photos_service.get_photo_by_id(photo_id)
    if not existing: raise HTTPException(status_code=404, detail="No encontrada")
    tags_list = None
    if tags:
        try: tags_list = json.loads(tags)
        except: tags_list = [t.strip() for t in tags.split(',') if t.strip()]
    data = {
        'title': title, 'description': description, 'year': year,
        'year_from': year_from, 'year_to': year_to, 'era': era, 'zone': zone,
        'lat': lat, 'lng': lng, 'source': source, 'author': author, 'rights': rights, 'tags': tags_list,
    }
    new_image_url = None
    new_thumb_url = None
    if image and image.filename:
        new_image_url, new_thumb_url = save_uploaded_image(image)
        data['image_url'] = new_image_url
        data['thumb_url'] = new_thumb_url
    try:
        updated = photos_service.update_photo(photo_id, data)
    except Exception:
        if new_image_url:
            _cleanup_upload(new_image_url, new_thumb_url)
        logger.exception("Error actualizando foto %s", photo_id)
        raise

    # Si la imagen cambio y el update fue ok, borrar la antigua
    if new_image_url and updated:
        _cleanup_upload(existing.image_url, existing.thumb_url)
    return updated


def _cleanup_upload(image_url: Optional[str], thumb_url: Optional[str]) -> None:
    """Elimina del disco los ficheros asociados a unas URLs /uploads/..."""
    for url in (image_url, thumb_url):
        if not url:
            continue
        # Convertir /uploads/xxx o /uploads/thumbs/xxx a ruta fisica
        rel = url.lstrip("/")
        if not rel.startswith("uploads/"):
            continue
        rel = rel[len("uploads/"):]
        path = os.path.join(UPLOADS_DIR, rel)
        try:
            if os.path.isfile(path):
                os.remove(path)
        except OSError as exc:
            logger.warning("No se pudo borrar %s: %s", path, exc)


@router.delete("/{photo_id:int}", response_model=MessageResponse)
@limiter.limit("20/minute")
async def delete_photo(request: Request, photo_id: int, current_user: TokenData = Depends(get_current_user)):
    existing = photos_service.get_photo_by_id(photo_id)
    if not existing: raise HTTPException(status_code=404, detail="No encontrada")
    if not photos_service.delete_photo(photo_id):
        raise HTTPException(status_code=500, detail="Error al eliminar")
    # Limpiar archivos asociados tras borrar registro
    _cleanup_upload(existing.image_url, existing.thumb_url)
    return MessageResponse(message=f"Foto {photo_id} eliminada", success=True)
