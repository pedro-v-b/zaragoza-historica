"""
Router para endpoints de artículos Wikipedia geolocalizados.
"""
from fastapi import APIRouter, Query

from services.wikipedia_service import wikipedia_service


router = APIRouter(prefix="/wikipedia", tags=["wikipedia"])


@router.get("")
async def get_wikipedia_articles(
    lat: float = Query(41.6488, description="Latitud del centro de búsqueda"),
    lon: float = Query(-0.8891, description="Longitud del centro de búsqueda"),
    radius: int = Query(10000, ge=100, le=10000, description="Radio en metros (máx 10km)"),
    limit: int = Query(200, ge=1, le=500, description="Número máximo de artículos"),
):
    """Obtiene artículos de Wikipedia geolocalizados cerca de unas coordenadas."""
    articles = wikipedia_service.get_articles(
        lat=lat,
        lon=lon,
        radius=radius,
        limit=limit,
    )
    return {"articles": articles, "total": len(articles)}
