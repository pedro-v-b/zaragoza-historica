import os

# Configuración
SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\photos_data.sql"
OUTPUT_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\photos_data_migrated.sql"
PUBLIC_URL_PREFIX = "https://ktnavneugmimhdvpnnga.supabase.co/storage/v1/object/public/uploads/"

def prepare_sql():
    try:
        print(f"Leyendo datos desde {SQL_FILE}...")
        # Usar encoding 'latin-1' para leer el archivo generado por Docker que tiene el error de ó
        with open(SQL_FILE, 'r', encoding='latin-1') as f:
            content = f.read()
        
        print("Corrigiendo URLs y extensiones...")
        # Corregir prefijos y extensiones
        content = content.replace("'/uploads/", f"'{PUBLIC_URL_PREFIX}")
        content = content.replace(".jpg'", ".webp'").replace(".png'", ".webp'")
        
        print(f"Guardando archivo procesado en {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print("\n--- ARCHIVO SQL LISTO PARA SUPABASE ---")
        
    except Exception as e:
        print(f"Error procesando SQL: {e}")

if __name__ == "__main__":
    prepare_sql()
