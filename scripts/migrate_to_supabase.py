import psycopg2
import os

# Configuración remota (Supabase)
REMOTE_DB = "postgresql://postgres:V4BG8aKwXi3qrNn@db.ktnavneugmimhdvpnnga.supabase.co:5432/postgres"

# Archivos locales
SCHEMA_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\backend_python\database\01_schema.sql"
SEEDS_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\backend_python\database\02_seeds.sql"

def run_migration():
    conn = None
    try:
        print("Conectando con Supabase...")
        conn = psycopg2.connect(REMOTE_DB)
        conn.autocommit = True
        cur = conn.cursor()
        
        # 1. Cargar Esquema
        print(f"Cargando esquema desde: {SCHEMA_FILE}")
        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
            cur.execute(f.read())
        print("Esquema creado con éxito.")
        
        # 2. Cargar Semillas (Fotos de ejemplo)
        print(f"Cargando semillas desde: {SEEDS_FILE}")
        with open(SEEDS_FILE, 'r', encoding='utf-8') as f:
            # Reemplazar extensiones .jpg por .webp en las semillas antes de insertar
            seeds_sql = f.read().replace('.jpg', '.webp').replace('.png', '.webp')
            cur.execute(seeds_sql)
        print("Semillas cargadas con éxito.")
        
        print("\n--- ¡MIGRACIÓN COMPLETADA CON ÉXITO! ---")
        
    except Exception as e:
        print(f"ERROR DURANTE LA MIGRACIÓN: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
