import os
import requests
import json
import re

# Configuración Supabase
SUPABASE_URL = "https://ktnavneugmimhdvpnnga.supabase.co"
SUPABASE_KEY = "sb_publishable_MjA3MDUyMjYtOGRhYy00ZjVkLTg3YzMtYjEwMjE0OWVhMmQw" # Usando la clave pública obtenida anteriormente
SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\final_upload.sql"

def parse_sql_to_json(sql_line):
    # Regex para extraer valores de: INSERT INTO public.photos VALUES (id, 'title', 'desc', ...)
    pattern = r"VALUES\s*\((.*)\);"
    match = re.search(pattern, sql_line, re.IGNORECASE)
    if not match:
        return None
    
    values_str = match.group(1)
    # Separar valores respetando las comas dentro de strings (comillas simples)
    # Esta es una aproximación simple, idealmente usaríamos un parser de SQL, 
    # pero para este formato concreto nos vale.
    
    # Un truco sucio pero efectivo: separar por ", '" y manejar los tipos
    # Pero los datos de Zaragoza tienen muchas comas en las descripciones.
    # Vamos a usar una técnica mejor: recorrer el string y detectar comas fuera de comillas.
    
    values = []
    current_val = []
    in_quotes = False
    i = 0
    while i < len(values_str):
        char = values_str[i]
        if char == "'" and (i == 0 or values_str[i-1] != "\\"):
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            values.append("".join(current_val).strip())
            current_val = []
            i += 1
            continue
        current_val.append(char)
        i += 1
    values.append("".join(current_val).strip())
    
    # Limpiar comillas y manejar NULLs
    def clean(v):
        if v.upper() == "NULL": return None
        if v.startswith("'") and v.endswith("'"):
            return v[1:-1].replace("''", "'") # Unescape single quotes
        try:
            if "." in v: return float(v)
            return int(v)
        except:
            return v

    clean_values = [clean(v) for v in values]
    
    # Mapear a nombres de columnas (basado en el esquema de photos)
    # schema: id, title, description, year, year_from, year_to, era, zone, lat, lng, geom, image_url, thumb_url, source, author, rights, tags, created_at, updated_at
    if len(clean_values) < 17:
        return None
        
    return {
        "id": clean_values[0],
        "title": clean_values[1],
        "description": clean_values[2],
        "year": clean_values[3],
        "year_from": clean_values[4],
        "year_to": clean_values[5],
        "era": clean_values[6],
        "zone": clean_values[7],
        "lat": clean_values[8],
        "lng": clean_values[9],
        # Saltamos geom (clean_values[10]) ya que Supabase lo genera o no lo necesitamos vía API REST simple
        "image_url": clean_values[11],
        "thumb_url": clean_values[12],
        "source": clean_values[13],
        "author": clean_values[14],
        "rights": clean_values[15],
        "tags": clean_values[16]
    }

def upload_all():
    print(f"Abriendo {SQL_FILE}...")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        lines = [l for l in f if 'INSERT INTO public.photos' in l]
    
    print(f"Procesando {len(lines)} registros...")
    data_to_upload = []
    for line in lines:
        obj = parse_sql_to_json(line)
        if obj:
            data_to_upload.append(obj)
    
    print(f"Subiendo {len(data_to_upload)} registros en bloques de 100...")
    # Usamos la API de Supabase vía PostgREST (endpoint /rest/v1/photos)
    # Nota: Requiere la Service Role Key para saltar RLS o que las políticas permitan inserción anónima
    # Como no tenemos la Service Key aquí, usaremos el método SQL vía MCP que es más directo.
    
    # Pero espera, ya tenemos un archivo SQL limpio en UTF-8. 
    # Voy a intentar subirlo usando el comando 'mcp_supabase_execute_sql' en bloques grandes.
    # El archivo final_upload.sql ya está en UTF-8 y corregido.
    pass

if __name__ == "__main__":
    # No ejecutaré el upload por API REST si puedo usar el SQL directo que es más potente
    print("Script de preparación cargado.")
