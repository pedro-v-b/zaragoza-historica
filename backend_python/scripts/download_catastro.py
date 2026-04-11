"""
Descarga y convierte edificios del Catastro INSPIRE (Zaragoza) a GeoJSON.
Requiere GDAL/ogr2ogr instalado.
"""
import os
import shutil
import ssl
import subprocess
import urllib.request
import zipfile
from urllib.error import URLError
from typing import Optional


CATASTRO_URL = "http://www.catastro.hacienda.gob.es/INSPIRE/Buildings/50/50900-ZARAGOZA/A.ES.SDGC.BU.50900.zip"
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "database", "catastro")
ZIP_PATH = os.path.join(DOWNLOAD_DIR, "buildings_zaragoza.zip")
GML_FILENAME = "A.ES.SDGC.BU.50900.building.gml"
GML_PATH = os.path.join(DOWNLOAD_DIR, GML_FILENAME)
GEOJSON_OUTPUT = os.path.join(DOWNLOAD_DIR, "buildings_zaragoza.geojson")


def _download_file(url: str, destination: str) -> None:
    """Descarga un fichero manejando problemas comunes de SSL en Windows."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python urllib",
        },
    )

    def _stream_with_opener(opener: urllib.request.OpenerDirector) -> None:
        with opener.open(req, timeout=120) as response, open(destination, "wb") as out:
            shutil.copyfileobj(response, out)

    try:
        _stream_with_opener(urllib.request.build_opener())
        return
    except URLError as exc:
        error_text = str(exc).lower()
        if "certificate verify failed" not in error_text:
            raise

    # Reintento usando certifi (útil en instalaciones de Python sin CA bundle configurado)
    try:
        import certifi  # type: ignore

        ctx = ssl.create_default_context(cafile=certifi.where())
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
        _stream_with_opener(opener)
        print("Descarga realizada usando CA bundle de certifi.")
        return
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Falló la verificación SSL. Instala certificados con:\n"
            "  C:/Users/pvial/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pip install certifi\n"
            "y vuelve a ejecutar el script."
        ) from exc


def _resolve_ogr2ogr() -> str:
    """Localiza ogr2ogr en PATH o en ubicaciones habituales de Windows."""
    env_path = os.getenv("OGR2OGR_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    in_path = shutil.which("ogr2ogr")
    if in_path:
        return in_path

    common_candidates = [
        r"C:\OSGeo4W\bin\ogr2ogr.exe",
        r"C:\OSGeo4W64\bin\ogr2ogr.exe",
        r"C:\Program Files\QGIS 3.34.0\bin\ogr2ogr.exe",
        r"C:\Program Files\QGIS 3.36.0\bin\ogr2ogr.exe",
        r"C:\Program Files\QGIS 3.38.0\bin\ogr2ogr.exe",
        r"C:\Program Files\QGIS 3.40.0\bin\ogr2ogr.exe",
        r"C:\Program Files\QGIS 3.42.0\bin\ogr2ogr.exe",
    ]
    for candidate in common_candidates:
        if os.path.exists(candidate):
            return candidate

    # Buscar cualquier instalación de QGIS en Program Files
    for base in (r"C:\Program Files", r"C:\Program Files (x86)"):
        if not os.path.isdir(base):
            continue
        try:
            entries = sorted(os.listdir(base), reverse=True)
        except OSError:
            continue
        for entry in entries:
            if not entry.startswith("QGIS "):
                continue
            candidate = os.path.join(base, entry, "bin", "ogr2ogr.exe")
            if os.path.exists(candidate):
                return candidate

    raise RuntimeError(
        "No se encontró 'ogr2ogr'. Instala GDAL/QGIS o define OGR2OGR_PATH apuntando a ogr2ogr.exe."
    )


def download() -> None:
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    if os.path.exists(ZIP_PATH):
        print(f"ZIP ya existe: {ZIP_PATH}")
        return
    print("Descargando edificios del Catastro (Zaragoza)...")
    _download_file(CATASTRO_URL, ZIP_PATH)
    print(f"Descargado: {ZIP_PATH}")


def extract() -> str:
    if os.path.exists(GML_PATH):
        print(f"GML ya existe: {GML_PATH}")
        return GML_PATH

    print("Extrayendo GML de edificios...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        gml_entry = None
        for name in zf.namelist():
            lower = name.lower()
            if lower.endswith("building.gml") and "buildingpart" not in lower:
                gml_entry = name
                break

        if not gml_entry:
            raise RuntimeError("No se encontró el fichero building.gml dentro del ZIP")

        extracted_path = zf.extract(gml_entry, DOWNLOAD_DIR)
        if os.path.abspath(extracted_path) != os.path.abspath(GML_PATH):
            os.makedirs(os.path.dirname(GML_PATH), exist_ok=True)
            if os.path.exists(GML_PATH):
                os.remove(GML_PATH)
            shutil.move(extracted_path, GML_PATH)

    print(f"Extraído: {GML_PATH}")
    return GML_PATH


def convert_to_geojson(gml_path: str) -> None:
    if os.path.exists(GEOJSON_OUTPUT):
        print(f"GeoJSON ya existe: {GEOJSON_OUTPUT}")
        return

    ogr2ogr_bin = _resolve_ogr2ogr()
    cmd = [
        ogr2ogr_bin,
        "-f", "GeoJSON",
        "-t_srs", "EPSG:4326",
        "-s_srs", "EPSG:25830",
        GEOJSON_OUTPUT,
        gml_path,
        "Building",
        "-lco", "COORDINATE_PRECISION=6",
    ]
    print("Convirtiendo GML a GeoJSON con ogr2ogr...")
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        print("Fallo con capa 'Building'. Reintentando sin capa explícita...")
        if exc.stderr:
            print(exc.stderr)
        cmd_alt = [
            ogr2ogr_bin,
            "-f", "GeoJSON",
            "-t_srs", "EPSG:4326",
            "-s_srs", "EPSG:25830",
            GEOJSON_OUTPUT,
            gml_path,
            "-lco", "COORDINATE_PRECISION=6",
        ]
        subprocess.run(cmd_alt, check=True)
    except FileNotFoundError:
        raise RuntimeError("No se encontró 'ogr2ogr'. Instala GDAL/QGIS y vuelve a ejecutar.")

    print(f"GeoJSON generado: {GEOJSON_OUTPUT}")


if __name__ == "__main__":
    download()
    gml = extract()
    convert_to_geojson(gml)
    print("Proceso completado.")
