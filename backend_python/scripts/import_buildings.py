"""
Importa el GML de edificios del Catastro Español (INSPIRE) a PostgreSQL/PostGIS.

Fuente : A.ES.SDGC.BU.50900.building.gml
Formato: GML 3.2, INSPIRE Building Data Specification v2
SRS     : EPSG:25830 → EPSG:4326 (WGS84)

Uso:
    python import_buildings.py [ruta_al_gml]

Si no se proporciona ruta busca:
    backend_python/database/catastro/A.ES.SDGC.BU.50900.building.gml

Dependencias extra (sólo para este script):
    pip install lxml pyproj
"""
import json
import os
import re
import sys
import time
from typing import Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from dotenv import load_dotenv  # noqa: E402
load_dotenv(os.path.join(BASE_DIR, ".env"))

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml no instalado → pip install lxml")

try:
    from pyproj import Transformer
except ImportError:
    sys.exit("ERROR: pyproj no instalado → pip install pyproj")

import psycopg2
from psycopg2.extras import execute_values

# ── Namespaces del GML del Catastro ─────────────────────────────────────────
BU_EXT2D  = "http://inspire.jrc.ec.europa.eu/schemas/bu-ext2d/2.0"
BU_CORE2D = "http://inspire.jrc.ec.europa.eu/schemas/bu-core2d/2.0"
GML       = "http://www.opengis.net/gml/3.2"
XSI       = "http://www.w3.org/2001/XMLSchema-instance"

TAG_BUILDING = f"{{{BU_EXT2D}}}Building"

# ── Reproyección EPSG:25830 → EPSG:4326 ─────────────────────────────────────
# always_xy=True: recibe (easting, northing) → devuelve (lon, lat)
_transformer = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)

# ── Configuración BD ─────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "zaragoza_historica"),
    "user":     os.getenv("DB_USER",     "zaragoza_user"),
    "password": os.getenv("DB_PASSWORD", "zaragoza_pass"),
}

GML_DEFAULT = os.path.join(
    BASE_DIR, "database", "catastro", "A.ES.SDGC.BU.50900.building.gml"
)
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema_buildings.sql")
BATCH_SIZE  = 500


# ── Extracción de campos ─────────────────────────────────────────────────────

def extract_year(elem) -> Optional[int]:
    """
    Extrae el año de construcción desde:
    bu-core2d:dateOfConstruction / DateOfEvent / beginning
    Valor esperado: '1980-01-01T00:00:00'  → 1980
    """
    path = (
        f"{{{BU_CORE2D}}}dateOfConstruction/"
        f"{{{BU_CORE2D}}}DateOfEvent/"
        f"{{{BU_CORE2D}}}beginning"
    )
    el = elem.find(path)
    if el is None or not (el.text or "").strip():
        return None
    m = re.match(r"(\d{4})", el.text.strip())
    if not m:
        return None
    year = int(m.group(1))
    return year if 1500 <= year <= 2030 else None


def extract_cadastral_ref(elem) -> Optional[str]:
    """
    Extrae la referencia catastral desde:
    bu-core2d:externalReference / ExternalReference / reference
    Fallback: gml:id del propio elemento (sin el prefijo 'ES.SDGC.BU.')
    """
    path = (
        f"{{{BU_CORE2D}}}externalReference/"
        f"{{{BU_CORE2D}}}ExternalReference/"
        f"{{{BU_CORE2D}}}reference"
    )
    el = elem.find(path)
    if el is not None and (el.text or "").strip():
        return el.text.strip()[:20]
    gml_id = elem.get(f"{{{GML}}}id", "")
    return gml_id.replace("ES.SDGC.BU.", "")[:20] or None


def extract_current_use(elem) -> Optional[str]:
    """Extrae bu-ext2d:currentUse y lo traduce a texto legible."""
    el = elem.find(f"{{{BU_EXT2D}}}currentUse")
    if el is None or not (el.text or "").strip():
        return None
    use_map = {
        "1_residential":      "Residencial",
        "2_agriculture":      "Agrícola",
        "3_industrial":       "Industrial",
        "4_1_office":         "Oficinas",
        "4_2_retail":         "Comercial",
        "4_3_publicServices": "Servicios públicos",
    }
    return use_map.get(el.text.strip(), el.text.strip())[:100]


def extract_int_field(elem, ns: str, local: str) -> Optional[int]:
    """Extrae un campo entero, devolviendo None si está marcado como nil."""
    el = elem.find(f"{{{ns}}}{local}")
    if el is None:
        return None
    if el.get(f"{{{XSI}}}nil") == "true" or el.get("nilReason"):
        return None
    try:
        return int(el.text.strip())
    except (TypeError, ValueError):
        return None


# ── Geometría ────────────────────────────────────────────────────────────────

def poslist_to_wgs84(text: str) -> list:
    """
    Convierte un gml:posList en UTM30N a lista de [lon, lat].
    Formato de entrada: 'easting1 northing1 easting2 northing2 ...'
    """
    nums = list(map(float, text.split()))
    coords = []
    for i in range(0, len(nums) - 1, 2):
        lon, lat = _transformer.transform(nums[i], nums[i + 1])
        coords.append([lon, lat])
    # Garantizar que el anillo esté cerrado
    if coords and coords[0] != coords[-1]:
        coords.append(coords[0])
    return coords


def extract_ring(ring_el) -> Optional[list]:
    """Extrae coordenadas de un gml:LinearRing → lista de [lon, lat]."""
    poslist = ring_el.find(f"{{{GML}}}posList")
    if poslist is None or not (poslist.text or "").strip():
        return None
    coords = poslist_to_wgs84(poslist.text.strip())
    return coords if len(coords) >= 4 else None


def extract_geometry(elem) -> Optional[dict]:
    """
    Extrae la geometría del edificio como GeoJSON MultiPolygon en WGS84.

    Ruta GML:
        bu-ext2d:geometry
          bu-core2d:BuildingGeometry
            bu-core2d:geometry
              gml:Surface
                gml:patches
                  gml:PolygonPatch  (puede haber varios por edificio)
                    gml:exterior / gml:LinearRing / gml:posList
                    gml:interior / gml:LinearRing / gml:posList  (huecos)
    """
    patches_el = elem.find(
        f"{{{BU_EXT2D}}}geometry/"
        f"{{{BU_CORE2D}}}BuildingGeometry/"
        f"{{{BU_CORE2D}}}geometry/"
        f"{{{GML}}}Surface/"
        f"{{{GML}}}patches"
    )
    if patches_el is None:
        return None

    polygons = []
    for patch in patches_el.findall(f"{{{GML}}}PolygonPatch"):
        ext_ring_el = patch.find(f"{{{GML}}}exterior/{{{GML}}}LinearRing")
        if ext_ring_el is None:
            continue
        ext_coords = extract_ring(ext_ring_el)
        if not ext_coords:
            continue

        rings = [ext_coords]
        for int_ring_el in patch.findall(f"{{{GML}}}interior/{{{GML}}}LinearRing"):
            int_coords = extract_ring(int_ring_el)
            if int_coords:
                rings.append(int_coords)

        polygons.append(rings)

    if not polygons:
        return None

    return {"type": "MultiPolygon", "coordinates": polygons}


# ── Base de datos ─────────────────────────────────────────────────────────────

def apply_schema(conn) -> None:
    """Aplica el esquema SQL (DROP + CREATE TABLE + índices)."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print("[OK] Esquema creado/renovado")


def insert_batch(conn, batch: list) -> None:
    sql = """
        INSERT INTO catastro_buildings
            (cadastral_ref, inspire_id, year_built, floors_above, floors_below,
             current_use, geometry)
        VALUES %s
    """
    template = """(
        %s, %s, %s, %s, %s, %s,
        ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
    )"""
    with conn.cursor() as cur:
        execute_values(cur, sql, batch, template=template, page_size=200)
    conn.commit()


# ── Procesado del GML ─────────────────────────────────────────────────────────

def process_gml(gml_path: str) -> None:
    size_mb = os.path.getsize(gml_path) / 1_048_576
    print(f"\n[*] GML: {gml_path}  ({size_mb:.1f} MB)")
    print("[*] Conectando a PostgreSQL...")

    conn = psycopg2.connect(**DB_CONFIG)
    print("[OK] Conectado")

    apply_schema(conn)

    t0 = time.perf_counter()
    total = skipped = 0
    batch: list = []

    # iterparse libera memoria elemento a elemento; tag= filtra directamente
    context = etree.iterparse(
        gml_path, events=("end",), tag=TAG_BUILDING, recover=True
    )

    for _event, elem in context:
        try:
            geom = extract_geometry(elem)
            if geom is None:
                skipped += 1
                continue

            batch.append((
                extract_cadastral_ref(elem),
                (elem.get(f"{{{GML}}}id") or "")[:100] or None,
                extract_year(elem),
                extract_int_field(elem, BU_EXT2D, "numberOfFloorsAboveGround"),
                None,                          # floors_below: no está en este GML
                extract_current_use(elem),
                json.dumps(geom),
            ))
            total += 1

            if len(batch) >= BATCH_SIZE:
                insert_batch(conn, batch)
                batch.clear()
                elapsed = time.perf_counter() - t0
                print(f"  Insertados: {total:>8,}   ({elapsed:.0f}s)", end="\r")

        except Exception as exc:
            skipped += 1
            if skipped <= 5:
                print(f"\n  [WARN] Edificio saltado ({type(exc).__name__}): {exc}")
        finally:
            elem.clear()
            # Liberar gml:featureMember anteriores para no acumular memoria.
            # elem es bu-ext2d:Building; su padre es gml:featureMember.
            feature_member = elem.getparent()
            if feature_member is not None:
                while feature_member.getprevious() is not None:
                    del feature_member.getparent()[0]

    if batch:
        insert_batch(conn, batch)

    conn.close()

    elapsed = time.perf_counter() - t0
    print(f"\n\n[OK] Importación completada en {elapsed:.1f}s")
    print(f"     Edificios importados : {total:,}")
    print(f"     Edificios saltados   : {skipped:,}")


if __name__ == "__main__":
    gml_path = sys.argv[1] if len(sys.argv) > 1 else GML_DEFAULT
    if not os.path.exists(gml_path):
        sys.exit(f"ERROR: Archivo no encontrado: {gml_path}")
    process_gml(gml_path)
