"""
Router para endpoints de edificios del Catastro.
"""
from typing import Optional

from fastapi import APIRouter, Query

from services.buildings_service import buildings_service


router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/geojson")
async def get_buildings_geojson(
    min_lng: float = Query(..., description="Longitud mínima del bbox"),
    min_lat: float = Query(..., description="Latitud mínima del bbox"),
    max_lng: float = Query(..., description="Longitud máxima del bbox"),
    max_lat: float = Query(..., description="Latitud máxima del bbox"),
    zoom: int = Query(15, ge=1, le=20),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    limit: int = Query(5000, ge=1, le=10000),
):
    return buildings_service.get_geojson(
        min_lng=min_lng,
        min_lat=min_lat,
        max_lng=max_lng,
        max_lat=max_lat,
        zoom=zoom,
        year_from=year_from,
        year_to=year_to,
        limit=limit,
    )


@router.get("/stats")
async def get_buildings_stats():
    return buildings_service.get_stats()
