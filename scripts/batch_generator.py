import os

INPUT_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\photos_data.sql"
PUBLIC_URL_PREFIX = "https://ktnavneugmimhdvpnnga.supabase.co/storage/v1/object/public/uploads/"

def get_batches(batch_size=100):
    try:
        print(f"Leyendo {INPUT_FILE} en formato UTF-16...")
        with open(INPUT_FILE, 'r', encoding='utf-16') as f:
            lines = [l for l in f if 'INSERT INTO' in l]
        
        for i in range(0, len(lines), batch_size):
            batch = lines[i:i+batch_size]
            sql = "".join(batch)
            sql = sql.replace("'/uploads/", f"'{PUBLIC_URL_PREFIX}")
            sql = sql.replace(".jpg'", ".webp'").replace(".png'", ".webp'")
            yield sql, i + len(batch), len(lines)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Este script solo genera los bloques, yo los ejecutaré manualmente para mayor control
    # Guardamos el primer bloque para probar
    gen = get_batches()
    sql, count, total = next(gen)
    with open(r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\batch_to_upload.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"Bloque preparado: {count}/{total}")
