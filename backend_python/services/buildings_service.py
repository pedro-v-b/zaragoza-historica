"""
Servicio para lógica de negocio de edificios del Catastro.
"""
import json
from typing import Optional

from repositories.buildings_repository import buildings_repository


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
        rows = buildings_repository.find_in_bbox(
            min_lng=min_lng,
            min_lat=min_lat,
            max_lng=max_lng,
            max_lat=max_lat,
            zoom=zoom,
            year_from=year_from,
            year_to=year_to,
            limit=limit,
        )

        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "geometry": json.loads(row["geojson"]),
                "properties": {
                    "id": row["id"],
                    "cadastral_ref": row["cadastral_ref"],
                    "year_built": row["year_built"],
                    "decade": row["decade"],
                    "current_use": row["current_use"],
                },
            })

        return {
            "type": "FeatureCollection",
            "features": features,
            "metadata": {
                "total": len(features),
                "bbox": [min_lng, min_lat, max_lng, max_lat],
                "zoom": zoom,
            },
        }

    def get_stats(self) -> dict:
        return buildings_repository.get_stats()


buildings_service = BuildingsService()
