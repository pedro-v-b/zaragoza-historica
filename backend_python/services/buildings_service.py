"""
Servicio para lógica de negocio de edificios del Catastro.
"""
import time
from collections import OrderedDict
from typing import Optional

from repositories.buildings_repository import buildings_repository


# Caché LRU de respuestas GeoJSON por (bbox redondeado, zoom, years)
_CACHE_TTL = 120  # 2 min
_CACHE_MAX = 128
_cache: "OrderedDict[tuple, tuple[float, dict]]" = OrderedDict()


def _round_bbox(v: float) -> float:
    # Redondea a ~11m (5 decimales) para agrupar peticiones casi idénticas.
    return round(v, 5)


class BuildingsService:
    """Servicio de edificios."""

    def get_geojson(
        self,
        min_lng: float,
        min_lat: float,
        max_lng: float,
        max_lat: float,
        zoom: int = 15,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        limit: int = 5000,
    ) -> dict:
        key = (
            _round_bbox(min_lng), _round_bbox(min_lat),
            _round_bbox(max_lng), _round_bbox(max_lat),
            zoom, year_from, year_to, limit,
        )
        now = time.time()

        cached = _cache.get(key)
        if cached and now - cached[0] < _CACHE_TTL:
            _cache.move_to_end(key)
            return cached[1]
        if cached:
            del _cache[key]

        fc = buildings_repository.find_geojson_in_bbox(
            min_lng=min_lng, min_lat=min_lat,
            max_lng=max_lng, max_lat=max_lat,
            zoom=zoom, year_from=year_from, year_to=year_to, limit=limit,
        )
        fc.setdefault("metadata", {
            "total": len(fc.get("features", [])),
            "bbox": [min_lng, min_lat, max_lng, max_lat],
            "zoom": zoom,
        })

        _cache[key] = (now, fc)
        _cache.move_to_end(key)
        while len(_cache) > _CACHE_MAX:
            _cache.popitem(last=False)
        return fc

    def get_stats(self) -> dict:
        return buildings_repository.get_stats()


buildings_service = BuildingsService()
