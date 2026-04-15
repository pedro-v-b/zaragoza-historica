import json
import os

INPUT_JSON = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\data_for_supabase.json"

def generate(start, count):
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    batch = data[start:start+count]
    json_str = json.dumps(batch, ensure_ascii=False).replace("'", "''")
    
    sql = f"""
INSERT INTO photos (id, title, description, year, year_from, year_to, era, zone, lat, lng, image_url, thumb_url, source, author, rights, tags, geometry)
SELECT id, title, description, year, year_from, year_to, era, zone, lat, lng, image_url, thumb_url, source, author, rights, tags, 
ST_SetSRID(ST_MakePoint(lng, lat), 4326)
FROM json_populate_recordset(null::photos, '{json_str}')
ON CONFLICT (id) DO NOTHING;
"""
    with open(rf"C:\Users\pvial\Desktop\TFG DAM v2\scripts\batch_{start}_{start+count}.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"Batch {start}-{start+count} generado.")

if __name__ == "__main__":
    import sys
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    generate(start, count)
