import os
import httpx
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor

# Configuración Supabase
PROJECT_REF = "ktnavneugmimhdvpnnga"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0bmF2bmV1Z21pbWhkdnBubmdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4OTg2NDIsImV4cCI6MjA5MTQ3NDY0Mn0.-opoLYwAWnDirmIK3mSektMBFBjzL584VqJE8eIlBKc"
BUCKET = "uploads"
BASE_URL = f"https://{PROJECT_REF}.supabase.co/storage/v1/object/{BUCKET}"

# Directorio local
LOCAL_DIR = Path(r"C:\Users\pvial\Desktop\TFG DAM v2\uploads")

HEADERS = {
    "Authorization": f"Bearer {ANON_KEY}",
    "apikey": ANON_KEY,
    "Content-Type": "image/webp"
}

def upload_file(file_path):
    # Calcular la ruta relativa para el Storage (ej: "foto.webp" o "thumbs/foto.webp")
    relative_path = file_path.relative_to(LOCAL_DIR).as_posix()
    url = f"{BASE_URL}/{relative_path}"
    
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            
        with httpx.Client() as client:
            response = client.post(url, headers=HEADERS, content=content)
            
        if response.status_code in [200, 201]:
            return "success"
        elif response.status_code == 400 and "already exists" in response.text:
            return "skipped"
        else:
            print(f"Error en {relative_path}: {response.status_code} - {response.text}")
            return "error"
    except Exception as e:
        print(f"Excepción en {relative_path}: {e}")
        return "error"

def main():
    # Buscar todos los archivos .webp en la carpeta de uploads y thumbs
    files = list(LOCAL_DIR.rglob("*.webp"))
    total = len(files)
    
    if total == 0:
        print("No se encontraron archivos .webp para subir.")
        return

    print(f"Iniciando subida de {total} archivos a Supabase Storage...")
    start_time = time.time()

    # Usar 20 hilos para subir varias fotos a la vez y terminar rápido
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(upload_file, files))

    end_time = time.time()
    success = results.count("success")
    skipped = results.count("skipped")
    errors = results.count("error")

    print(f"\n--- Resumen de Subida ---")
    print(f"Subidos con éxito: {success}")
    print(f"Ya existían (saltados): {skipped}")
    print(f"Errores: {errors}")
    print(f"Tiempo total: {end_time - start_time:.2f} segundos")

if __name__ == "__main__":
    main()
