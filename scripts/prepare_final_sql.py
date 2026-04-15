import os

INPUT_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\photos_data.sql"
OUTPUT_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\final_upload.sql"
PUBLIC_URL_PREFIX = "https://ktnavneugmimhdvpnnga.supabase.co/storage/v1/object/public/uploads/"

def prepare_all():
    try:
        print(f"Leyendo registros reales en UTF-16...")
        with open(INPUT_FILE, 'r', encoding='utf-16') as f:
            lines = [l for l in f if 'INSERT INTO public.photos' in l]
        
        print(f"Procesando {len(lines)} registros...")
        all_sql = "".join(lines)
        all_sql = all_sql.replace("'/uploads/", f"'{PUBLIC_URL_PREFIX}")
        all_sql = all_sql.replace(".jpg'", ".webp'").replace(".png'", ".webp'")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(all_sql)
            
        print(f"Archivo listo: {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    prepare_all()
