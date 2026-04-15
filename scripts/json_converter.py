import os
import json
import re

SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\final_upload.sql"
OUTPUT_JSON = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\data_for_supabase.json"

def parse_sql_to_dict(sql_line):
    pattern = r"VALUES\s*\((.*)\);"
    match = re.search(pattern, sql_line, re.IGNORECASE)
    if not match: return None
    
    values_str = match.group(1)
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
    
    def clean(v):
        if v.upper() == "NULL": return None
        if v.startswith("'") and v.endswith("'"):
            return v[1:-1].replace("''", "'")
        try:
            if "." in v: return float(v)
            return int(v)
        except: return v

    cv = [clean(v) for v in values]
    if len(cv) < 17: return None
    
    # Procesar tags: si es string lo convertimos a lista
    tags = cv[16]
    if isinstance(tags, str):
        # El formato de postgres para arrays es {tag1,tag2}
        tags = tags.strip('{}').split(',') if tags.startswith('{') else [tags]
    elif tags is None:
        tags = []

    return {
        "id": cv[0],
        "title": cv[1],
        "description": cv[2],
        "year": cv[3],
        "year_from": cv[4],
        "year_to": cv[5],
        "era": cv[6],
        "zone": cv[7],
        "lat": cv[8],
        "lng": cv[9],
        "image_url": cv[11],
        "thumb_url": cv[12],
        "source": cv[13],
        "author": cv[14],
        "rights": cv[15],
        "tags": tags
    }

def convert():
    print("Leyendo SQL...")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        lines = [l for l in f if 'INSERT INTO public.photos' in l]
    
    print(f"Procesando {len(lines)} registros...")
    data = []
    for line in lines:
        obj = parse_sql_to_dict(line)
        if obj: data.append(obj)
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"JSON guardado: {OUTPUT_JSON}")

if __name__ == "__main__":
    convert()
