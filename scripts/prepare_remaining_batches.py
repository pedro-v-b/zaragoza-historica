import os
import requests
import json

# Configuración API Supabase
SUPABASE_URL = "https://ktnavneugmimhdvpnnga.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") # Lo obtendré del entorno
SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\final_upload.sql"

def upload_remaining():
    try:
        print(f"Leyendo registros de {SQL_FILE}...")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            # Saltamos los primeros 200 que ya subimos
            lines = [l for l in f if 'INSERT INTO public.photos' in l][200:]
        
        total = len(lines)
        print(f"Subiendo {total} registros restantes...")
        
        # Usar el endpoint de SQL de Supabase vía REST si fuera posible, 
        # pero como tengo la herramienta MCP, mejor lo hago en bloques aquí
        # Preparar bloques de 200 para que el usuario los ejecute o yo mismo
        for i in range(0, total, 200):
            batch = lines[i:i+200]
            with open(f"C:\\Users\\pvial\\Desktop\\TFG DAM v2\\scripts\\batch_{i//200 + 2}.sql", "w", encoding="utf-8") as out:
                out.write("".join(batch))
        
        print(f"Se han generado {total//200 + 1} archivos de bloque.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    upload_remaining()
