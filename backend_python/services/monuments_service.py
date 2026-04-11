"""
Servicio para obtener monumentos y patrimonio cultural de Zaragoza.
Usa la API de Datos Abiertos del Ayuntamiento de Zaragoza con caché en memoria.
"""
import time
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)

_cache: dict = {}
CACHE_TTL = 86400  # 24 horas (los monumentos no cambian frecuentemente)

API_URL = "https://www.zaragoza.es/sede/servicio/monumento.json"
USER_AGENT = "ZaragozaHistorica/1.0 (TFG DAM)"


class MonumentsService:

    def get_monuments(self) -> list:
        now = time.time()
        if "all" in _cache:
            cached_time, cached_data = _cache["all"]
            if now - cached_time < CACHE_TTL:
                return cached_data

        monuments = self._fetch()
        _cache["all"] = (now, monuments)
        return monuments

    def _fetch(self) -> list:
        params = urllib.parse.urlencode({
            "rows": "500",
            "srsname": "wgs84",
        })
        url = f"{API_URL}?{params}"

        req = urllib.request.Request(url)
        req.add_header("User-Agent", USER_AGENT)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read())
        except Exception as e:
            logger.error("Error fetching monuments: %s", e)
            return []

        results = data.get("result", [])
        monuments = []
        for item in results:
            geometry = item.get("geometry")
            if not geometry:
                continue
            coords = geometry.get("coordinates", [])
            if len(coords) < 2:
                continue

            monuments.append({
                "id": item.get("id"),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "estilo": item.get("estilo", ""),
                "datacion": item.get("datacion", ""),
                "address": item.get("address", ""),
                "horario": item.get("horario", ""),
                "image": item.get("image"),
                "url": item.get("uri", ""),
                "lon": coords[0],
                "lat": coords[1],
            })

        return monuments


monuments_service = MonumentsService()
