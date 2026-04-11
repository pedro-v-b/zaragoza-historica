#!/usr/bin/env python3
"""
Flickr Photostream Scraper
Descarga imágenes y metadatos del photostream de Flickr para proyectos de mapeo geoespacial.

Uso: python flickr_scraper.py
"""

import os
import re
import json
import time
import requests
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging

# Configuración
BASE_URL = "https://www.flickr.com"
USER = "zaragozaantigua"
PHOTOSTREAM_URL = f"https://www.flickr.com/photos/{USER}/"
OUTPUT_DIR = Path("FLICKR_GEO_DATA")
IMAGES_DIR = OUTPUT_DIR / "images"
METADATA_FILE = OUTPUT_DIR / "metadata.json"

# Headers para simular navegador
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

# Configuración de reintentos
MAX_RETRIES = 3
RETRY_DELAY = 2
REQUEST_DELAY = 0.5

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PhotoMetadata:
    """Estructura de metadatos de una foto."""
    id: str
    album_title: str
    filename: str
    title: str
    description: str
    capture_year: Optional[int]
    geolocation: Optional[Dict[str, float]]
    tags: List[str]
    flickr_url: str


class FlickrScraper:
    """Scraper para photostream de Flickr."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.images_dir = output_dir / "images"
        self.metadata_file = output_dir / "metadata.json"
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.processed_ids: Set[str] = set()
        self.metadata: List[Dict] = []

        # Crear directorios
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Cargar metadatos existentes para reanudar
        self._load_existing_metadata()

    def _load_existing_metadata(self):
        """Carga metadatos existentes para permitir reanudación."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    self.processed_ids = {photo['id'] for photo in self.metadata}
                    logger.info(f"Cargados {len(self.processed_ids)} fotos ya procesadas")
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error al cargar metadatos existentes: {e}")
                self.metadata = []
                self.processed_ids = set()

    def _save_metadata(self):
        """Guarda los metadatos al archivo JSON."""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def _request_with_retry(self, url: str, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
        """Realiza una petición HTTP con reintentos."""
        for attempt in range(retries):
            try:
                time.sleep(REQUEST_DELAY)
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return response
                elif response.status_code == 404:
                    return None  # Página no existe
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt + 1}/{retries} fallido para {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        return None

    def get_all_photo_ids(self) -> List[str]:
        """Obtiene todos los IDs de fotos del photostream."""
        logger.info("Recopilando IDs de fotos del photostream...")
        photo_ids = set()
        page = 1
        consecutive_empty = 0

        with tqdm(desc="Escaneando páginas", unit="pág") as pbar:
            while consecutive_empty < 3:
                url = f"{PHOTOSTREAM_URL}page{page}/" if page > 1 else PHOTOSTREAM_URL
                response = self._request_with_retry(url)

                if not response:
                    consecutive_empty += 1
                    page += 1
                    pbar.update(1)
                    continue

                html = response.text

                # Buscar IDs de fotos
                ids_found = set(re.findall(rf'/photos/{USER}/(\d{{10,}})', html))
                ids_found.update(re.findall(r'"id":"(\d{10,})"', html))

                new_ids = ids_found - photo_ids
                if not new_ids:
                    consecutive_empty += 1
                else:
                    consecutive_empty = 0
                    photo_ids.update(new_ids)

                pbar.update(1)
                pbar.set_postfix({'fotos': len(photo_ids), 'página': page})
                page += 1

                # Límite de seguridad
                if page > 500:
                    break

        logger.info(f"Total de IDs de fotos encontrados: {len(photo_ids)}")
        return list(photo_ids)

    def get_photo_metadata(self, photo_id: str) -> Optional[Dict]:
        """Extrae los metadatos de una foto individual."""
        url = f"{BASE_URL}/photos/{USER}/{photo_id}/"
        response = self._request_with_retry(url)

        if not response:
            return None

        html = response.text
        data = {}

        # Título desde og:title
        og_title = re.search(r'property="og:title" content="([^"]+)"', html)
        if og_title:
            data['title'] = og_title.group(1)
        else:
            title_match = re.search(r'<title>([^|<]+)', html)
            data['title'] = title_match.group(1).strip() if title_match else ''

        # Descripción desde og:description
        og_desc = re.search(r'property="og:description" content="([^"]+)"', html)
        if og_desc:
            data['description'] = og_desc.group(1)
        else:
            data['description'] = ''

        # Año histórico en el título o descripción (1800-1999)
        text_to_search = f"{data.get('title', '')} {data.get('description', '')}"
        historical_years = re.findall(r'\b(1[89]\d{2})\b', text_to_search)
        if historical_years:
            data['capture_year'] = min(int(y) for y in historical_years)
        else:
            data['capture_year'] = None

        # Geolocalización
        geo_match = re.search(r'"latitude":([\d.-]+).*?"longitude":([\d.-]+)', html)
        if geo_match:
            try:
                lat = float(geo_match.group(1))
                lng = float(geo_match.group(2))
                if 40 < lat < 43 and -2 < lng < 1:  # Verificar coordenadas cerca de Zaragoza
                    data['geolocation'] = {'latitude': lat, 'longitude': lng}
                else:
                    data['geolocation'] = None
            except ValueError:
                data['geolocation'] = None
        else:
            data['geolocation'] = None

        # Tags
        raw_tags = re.findall(r'"raw":"([^"]+)"', html)
        data['tags'] = [t for t in set(raw_tags) if len(t) < 50 and not t.startswith('http')]

        data['flickr_url'] = url
        return data

    def get_original_image_url(self, photo_id: str) -> Optional[str]:
        """Obtiene la URL de la imagen en tamaño ORIGINAL."""
        # Primero intentar la página de tamaño original
        sizes_url = f"{BASE_URL}/photos/{USER}/{photo_id}/sizes/o/"
        response = self._request_with_retry(sizes_url)

        if response:
            # Buscar URL de imagen original (_o)
            match = re.search(r'(https://live\.staticflickr\.com/[^"\']+_o\.[a-z]+)', response.text)
            if match:
                return match.group(1)

            # También buscar en el enlace de descarga
            download_match = re.search(r'href="(https://[^"]+)"[^>]*>Download', response.text, re.IGNORECASE)
            if download_match:
                return download_match.group(1)

        # Si no hay original, intentar tamaños grandes en orden
        for size_code in ['6k', '5k', '4k', '3k', 'k', 'h', 'l', 'c', 'z']:
            sizes_url = f"{BASE_URL}/photos/{USER}/{photo_id}/sizes/{size_code}/"
            response = self._request_with_retry(sizes_url)

            if response and response.status_code == 200:
                # Buscar URL de imagen
                pattern = rf'(https://live\.staticflickr\.com/[^"\']+_{size_code}\.[a-z]+)'
                match = re.search(pattern, response.text)
                if match:
                    return match.group(1)

        # Último recurso: página principal
        photo_url = f"{BASE_URL}/photos/{USER}/{photo_id}/"
        response = self._request_with_retry(photo_url)
        if response:
            # Buscar la imagen más grande disponible
            matches = re.findall(r'(https://live\.staticflickr\.com/\d+/\d+_[a-f0-9]+(?:_[a-z0-9]+)?\.[a-z]+)', response.text)
            if matches:
                # Priorizar por sufijo de tamaño
                for suffix in ['_o', '_6k', '_5k', '_4k', '_3k', '_k', '_h', '_l', '_c', '_z', '_n', '_m', '_s']:
                    for url in matches:
                        if suffix + '.' in url:
                            return url
                return matches[0]

        return None

    def download_image(self, url: str, filename: str) -> bool:
        """Descarga una imagen y la guarda en el directorio de imágenes."""
        filepath = self.images_dir / filename

        if filepath.exists():
            return True  # Ya descargada

        try:
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True
        except Exception as e:
            logger.error(f"Error descargando imagen {filename}: {e}")
            return False

    def process_photo(self, photo_id: str) -> Optional[PhotoMetadata]:
        """Procesa una foto individual: extrae metadatos y descarga imagen."""
        if photo_id in self.processed_ids:
            return None

        # Obtener metadatos
        metadata = self.get_photo_metadata(photo_id)
        if not metadata:
            logger.warning(f"No se pudieron obtener metadatos para foto {photo_id}")
            return None

        # Obtener URL de imagen original
        image_url = self.get_original_image_url(photo_id)
        if not image_url:
            logger.warning(f"No se pudo obtener URL de imagen para foto {photo_id}")
            return None

        # Determinar extensión y nombre de archivo
        ext_match = re.search(r'\.([a-z]+)$', image_url, re.IGNORECASE)
        ext = ext_match.group(1) if ext_match else 'jpg'
        filename = f"{photo_id}.{ext}"

        # Descargar imagen
        if not self.download_image(image_url, filename):
            logger.warning(f"No se pudo descargar imagen para foto {photo_id}")

        # Crear objeto de metadatos
        photo_metadata = PhotoMetadata(
            id=photo_id,
            album_title="Photostream",
            filename=filename,
            title=metadata['title'],
            description=metadata['description'],
            capture_year=metadata['capture_year'],
            geolocation=metadata['geolocation'],
            tags=metadata['tags'],
            flickr_url=metadata['flickr_url']
        )

        return photo_metadata

    def run(self):
        """Ejecuta el proceso completo de scraping."""
        logger.info("=" * 60)
        logger.info("FLICKR PHOTOSTREAM SCRAPER")
        logger.info(f"Usuario: {USER}")
        logger.info("=" * 60)

        # Fase 1: Recopilar IDs de fotos
        all_photo_ids = self.get_all_photo_ids()

        if not all_photo_ids:
            logger.error("No se encontraron fotos")
            return

        # Filtrar fotos ya procesadas
        photos_to_process = [pid for pid in all_photo_ids if pid not in self.processed_ids]
        logger.info(f"Fotos pendientes de procesar: {len(photos_to_process)}")

        if not photos_to_process:
            logger.info("Todas las fotos ya han sido procesadas")
            return

        # Fase 2: Procesar cada foto
        logger.info("Procesando fotos (metadatos + descarga en tamaño original)...")

        success_count = 0
        error_count = 0

        for photo_id in tqdm(photos_to_process, desc="Descargando fotos", unit="foto"):
            try:
                result = self.process_photo(photo_id)

                if result:
                    self.metadata.append(asdict(result))
                    self.processed_ids.add(photo_id)
                    success_count += 1

                    # Guardar progreso cada 10 fotos
                    if success_count % 10 == 0:
                        self._save_metadata()
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Error procesando foto {photo_id}: {e}")
                error_count += 1

        # Guardar metadatos finales
        self._save_metadata()

        # Resumen final
        logger.info("=" * 60)
        logger.info("RESUMEN")
        logger.info("=" * 60)
        logger.info(f"Total de fotos procesadas correctamente: {success_count}")
        logger.info(f"Total de errores: {error_count}")
        logger.info(f"Total de fotos en metadata.json: {len(self.metadata)}")
        logger.info(f"Imágenes guardadas en: {self.images_dir}")
        logger.info(f"Metadatos guardados en: {self.metadata_file}")


def main():
    """Punto de entrada principal."""
    scraper = FlickrScraper(output_dir=OUTPUT_DIR)
    scraper.run()


if __name__ == "__main__":
    main()
