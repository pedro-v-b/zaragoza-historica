"""
Modelos Pydantic para validación y serialización
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Photo(BaseModel):
    """Modelo de foto histórica"""
    id: int
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    era: Optional[str] = None
    zone: Optional[str] = None
    lat: float
    lng: float
    image_url: str
    thumb_url: str
    source: Optional[str] = None
    author: Optional[str] = None
    rights: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PhotoFilters(BaseModel):
    """Filtros para búsqueda de fotos"""
    bbox: Optional[str] = Field(None, description="Bounding box: 'minLng,minLat,maxLng,maxLat'")
    yearFrom: Optional[int] = Field(None, alias="yearFrom")
    yearTo: Optional[int] = Field(None, alias="yearTo")
    era: Optional[str] = None
    zone: Optional[str] = None
    q: Optional[str] = Field(None, description="Búsqueda de texto")
    page: int = Field(1, ge=1)
    pageSize: int = Field(20, ge=1, le=100, alias="pageSize")

    class Config:
        populate_by_name = True


class PaginatedPhotos(BaseModel):
    """Respuesta paginada de fotos"""
    items: List[Photo]
    total: int
    page: int
    pageSize: int = Field(alias="pageSize")
    totalPages: int = Field(alias="totalPages")

    class Config:
        populate_by_name = True


class Bounds(BaseModel):
    """Límites geográficos de una capa"""
    north: float
    south: float
    east: float
    west: float


class MapLayer(BaseModel):
    """Capa del mapa"""
    id: int
    name: str
    year: Optional[int] = None
    type: Literal['plan', 'ortho', 'current']
    tile_url_template: Optional[str] = None
    attribution: Optional[str] = None
    min_zoom: int = Field(alias="min_zoom")
    max_zoom: int = Field(alias="max_zoom")
    bounds: Optional[Bounds] = None
    is_active: bool = Field(alias="is_active")
    display_order: int = Field(alias="display_order")

    class Config:
        populate_by_name = True
        from_attributes = True


class FilterMetadata(BaseModel):
    """Metadatos para filtros dinámicos"""
    eras: List[str]
    zones: List[str]
    yearRange: dict = Field(alias="yearRange")

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    """Respuesta del health check"""
    status: str
    timestamp: datetime


# ============== AUTH SCHEMAS ==============

class LoginRequest(BaseModel):
    """Request para login"""
    username: str = Field(..., min_length=1, description="Nombre de usuario")
    password: str = Field(..., min_length=1, description="Contraseña")


class TokenData(BaseModel):
    """Datos extraídos del token JWT"""
    username: str
    user_id: int
    role: str = "user"


class UserResponse(BaseModel):
    """Respuesta con datos del usuario (sin contraseña)"""
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Respuesta de login exitoso"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje"""
    message: str
    success: bool = True
