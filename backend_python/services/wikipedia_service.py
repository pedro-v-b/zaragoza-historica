"""
Servicio para obtener artículos de Wikipedia geolocalizados.
Usa la API de Wikipedia (geosearch) y cachea resultados en memoria.
"""
import time
import urllib.request
import urllib.parse
import json
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


# Caché en memoria: clave = "lat,lon,radius" → (timestamp, datos)
_cache: dict[str, tuple[float, list]] = {}
CACHE_TTL = 3600  # 1 hora


class WikipediaService:
    """Servicio de artículos Wikipedia geolocalizados."""

    API_URL = "https://es.wikipedia.org/w/api.php"
    USER_AGENT = "ZaragozaHistorica/1.0 (TFG DAM)"

    def get_articles(
        self,
        lat: float,
        lon: float,
        radius: int = 10000,
        limit: int = 200,
    ) -> List[dict]:
        """Obtiene artículos de Wikipedia cercanos a unas coordenadas."""

        cache_key = f"{lat:.4f},{lon:.4f},{radius}"
        now = time.time()

        # Comprobar caché
        if cache_key in _cache:
            cached_time, cached_data = _cache[cache_key]
            if now - cached_time < CACHE_TTL:
                return cached_data[:limit]

        # Llamar a la API de Wikipedia
        articles = self._fetch_from_wikipedia(lat, lon, radius, limit)

        # Guardar en caché
        _cache[cache_key] = (now, articles)

        return articles

    def _fetch_from_wikipedia(
        self,
        lat: float,
        lon: float,
        radius: int,
        limit: int,
    ) -> List[dict]:
        """Hace la petición real a la API de Wikipedia."""

        # Limitar a 500 (máximo de la API)
        api_limit = min(limit, 500)

        params = {
            "action": "query",
            "generator": "geosearch",
            "ggscoord": f"{lat}|{lon}",
            "ggsradius": str(min(radius, 10000)),
            "ggslimit": str(api_limit),
            "prop": "coordinates|pageimages|extracts|info",
            "piprop": "thumbnail",
            "pithumbsize": "300",
            "exintro": "true",
            "explaintext": "true",
            "exlimit": str(api_limit),
            "inprop": "url",
            "format": "json",
        }

        url = f"{self.API_URL}?{urllib.parse.urlencode(params)}"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", self.USER_AGENT)
        req.add_header("Accept-Encoding", "gzip")

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                # Manejar respuesta gzip
                if response.headers.get("Content-Encoding") == "gzip":
                    import gzip
                    data = gzip.decompress(response.read())
                else:
                    data = response.read()

                result = json.loads(data)
        except Exception as e:
            logger.error("Error fetching Wikipedia articles: %s", e)
            return []

        pages = result.get("query", {}).get("pages", {})
        if not pages:
            return []

        articles = []
        for page in pages.values():
            coords = page.get("coordinates", [{}])
            coord = coords[0] if coords else {}

            thumbnail = page.get("thumbnail")

            article = {
                "pageid": page.get("pageid"),
                "title": page.get("title", ""),
                "lat": coord.get("lat"),
                "lon": coord.get("lon"),
                "extract": page.get("extract", ""),
                "url": page.get("fullurl", ""),
                "thumbnail": thumbnail.get("source") if thumbnail else None,
            }

            # Solo incluir si tiene coordenadas válidas
            if article["lat"] is not None and article["lon"] is not None:
                articles.append(article)

        # Ordenar por distancia al centro (aproximada)
        articles.sort(
            key=lambda a: (a["lat"] - lat) ** 2 + (a["lon"] - lon) ** 2
        )

        return articles


wikipedia_service = WikipediaService()
