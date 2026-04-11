#!/usr/bin/env python3
"""
Importador de fotos de Flickr a Zaragoza Historica
Genera SQL y copia imagenes para importar al sistema TFG.
"""

import os
import json
import shutil
import re
import html
from pathlib import Path
from PIL import Image
from tqdm import tqdm

# Configuracion
METADATA_FILE = Path(r"C:\Users\pvial\flickr_scraper\metadata.json")
TFG_DIR = Path(r"C:\Users\pvial\Desktop\TFG DAM v2")
UPLOADS_DIR = TFG_DIR / "uploads"
THUMBS_DIR = UPLOADS_DIR / "thumbs"
SQL_FILE = TFG_DIR / "flickr_import.sql"

# Tamano de miniaturas
THUMB_SIZE = (400, 400)


def get_era_from_year(year):
    """Determina la era basandose en el ano."""
    if not year:
        return None
    if year < 1900:
        return "Siglo XIX"
    elif year < 1910:
        return "Anos 1900"
    elif year < 1920:
        return "Anos 10"
    elif year < 1930:
        return "Anos 20"
    elif year < 1940:
        return "Anos 30"
    elif year < 1950:
        return "Anos 40"
    elif year < 1960:
        return "Anos 50"
    elif year < 1970:
        return "Anos 60"
    elif year < 1980:
        return "Anos 70"
    elif year < 1990:
        return "Anos 80"
    elif year < 2000:
        return "Anos 90"
    else:
        return "Siglo XXI"


def parse_year_range_from_album(album_title):
    """Extrae rango de anos del titulo del album (ej: '1900-1909')."""
    if not album_title:
        return None, None
    match = re.match(r'(\d{4})-(\d{4})', album_title)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def clean_description(desc):
    """Limpia la descripcion de HTML entities y texto extra."""
    if not desc:
        return ""
    # Decodificar HTML entities
    desc = html.unescape(desc)
    # Eliminar URLs
    desc = re.sub(r'https?://\S+', '', desc)
    # Eliminar menciones al proyecto GAZA
    desc = re.sub(r'Proyecto GAZA.*$', '', desc, flags=re.DOTALL)
    # Limpiar espacios multiples
    desc = re.sub(r'\s+', ' ', desc).strip()
    return desc[:2000] if desc else ""


def escape_sql(text):
    """Escapa texto para SQL."""
    if text is None:
        return "NULL"
    text = str(text).replace("'", "''")
    return f"'{text}'"


def find_image_file(photo_id):
    """Verifica si el archivo de imagen existe en uploads."""
    for ext in ['.jpg', '.jpeg', '.png', '.gif']:
        img_path = UPLOADS_DIR / f"{photo_id}{ext}"
        if img_path.exists():
            return img_path
    return None


def create_thumbnail(src_path, dest_path):
    """Crea una miniatura de la imagen si no existe."""
    if dest_path.exists():
        return True
    try:
        with Image.open(src_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.thumbnail(THUMB_SIZE, Image.Resampling.LANCZOS)
            img.save(dest_path, "JPEG", quality=85)
        return True
    except Exception as e:
        return False


def load_metadata():
    """Carga los metadatos de Flickr."""
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def filter_geolocated(photos):
    """Filtra solo las fotos con geolocalizacion."""
    return [p for p in photos if p.get('geolocation') is not None]


def main():
    print("=" * 60)
    print("IMPORTADOR FLICKR -> ZARAGOZA HISTORICA")
    print("=" * 60)

    # Cargar metadatos
    print("\nCargando metadatos...")
    all_photos = load_metadata()
    print(f"Total de fotos en metadata.json: {len(all_photos)}")

    # Filtrar fotos con geolocalizacion
    geolocated = filter_geolocated(all_photos)
    print(f"Fotos con geolocalizacion: {len(geolocated)}")

    if not geolocated:
        print("No hay fotos con geolocalizacion para importar")
        return

    # Generar SQL
    sql_statements = []
    imported = 0
    errors = 0
    missing = 0

    for photo in tqdm(geolocated, desc="Procesando fotos", unit="foto"):
        try:
            # Verificar si la imagen existe en uploads
            img_path = find_image_file(photo['id'])
            if not img_path:
                missing += 1
                continue

            filename = img_path.name
            thumb_path = THUMBS_DIR / filename

            # Asegurar que existe miniatura
            if not thumb_path.exists():
                create_thumbnail(img_path, thumb_path)

            # Preparar datos
            geo = photo['geolocation']
            
            # Priorizar datos ya extraídos del título en el paso anterior
            capture_year = photo.get('capture_year')
            year_from = photo.get('year_from')
            year_to = photo.get('year_to')
            
            # Si no hay datos del título, intentar del álbum (como fallback)
            if not capture_year:
                album_from, album_to = parse_year_range_from_album(photo.get('album_title', ''))
                if album_from and album_to:
                    year_from = album_from
                    year_to = album_to
                    capture_year = (album_from + album_to) // 2
            
            era = get_era_from_year(capture_year)

            # Tags como array PostgreSQL
            tags = photo.get('tags', [])
            if tags:
                tags_sql = "ARRAY[" + ",".join([escape_sql(t) for t in tags]) + "]"
            else:
                tags_sql = "NULL"

            # Generar SQL INSERT
            sql = f"""INSERT INTO photos (title, description, year, year_from, year_to, era, lat, lng, image_url, thumb_url, source, author, rights, tags)
VALUES ({escape_sql(photo['title'][:255])}, {escape_sql(clean_description(photo.get('description', '')))}, {capture_year if capture_year else 'NULL'}, {year_from if year_from else 'NULL'}, {year_to if year_to else 'NULL'}, {escape_sql(era)}, {geo['latitude']}, {geo['longitude']}, {escape_sql(f'/uploads/{filename}')}, {escape_sql(f'/uploads/thumbs/{filename}')}, {escape_sql(photo['flickr_url'])}, 'Zaragoza Antigua (Flickr)', 'Uso educativo', {tags_sql});"""

            sql_statements.append(sql)
            imported += 1

        except Exception as e:
            errors += 1
            print(f"\nError procesando {photo['id']}: {e}")

    # Guardar SQL
    print(f"\nGuardando {len(sql_statements)} sentencias SQL...")
    with open(SQL_FILE, 'w', encoding='utf-8') as f:
        f.write("-- Importacion de fotos de Flickr\n")
        f.write("-- Generado automaticamente\n\n")
        f.write("BEGIN;\n\n")
        for sql in sql_statements:
            f.write(sql + "\n")
        f.write("\nCOMMIT;\n")

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"Fotos con geolocalizacion: {len(geolocated)}")
    print(f"Fotos encontradas e importadas: {imported}")
    print(f"Fotos no encontradas en uploads: {missing}")
    print(f"Errores: {errors}")
    print(f"Archivo SQL generado: {SQL_FILE}")
    print("\nPara importar a la base de datos, ejecuta:")
    print(f'docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < "{SQL_FILE}"')


if __name__ == "__main__":
    main()

