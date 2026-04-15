import json
import requests
import time

# Configuración
INPUT_JSON = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\data_for_supabase.json"
# Nota: La URL de SQL de Supabase vía MCP usa una API interna. 
# Para este script usaremos la API REST de Supabase que es estándar.
SUPABASE_URL = "https://ktnavneugmimhdvpnnga.supabase.co/rest/v1/photos"
# Necesitas la Service Role Key para saltar RLS. 
# Como no la tengo, generaré un archivo SQL por bloques para que lo pegues en el panel de Supabase si prefieres,
# o intentaremos con la anon key si las políticas lo permiten.
ANON_KEY = "sb_publishable_MjA3MDUyMjYtOGRhYy00ZjVkLTg3YzMtYjEwMjE0OWVhMmQw"

def upload():
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = len(data)
    # Empezamos desde el 30 que es el último que subí
    batch_size = 50
    
    print(f"Iniciando subida de {total - 30} registros...")
    
    headers = {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {ANON_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    for i in range(30, total, batch_size):
        batch = data[i:i+batch_size]
        # Añadir la geometría en el JSON para que la API REST la procese
        # Nota: PostgREST acepta GeoJSON o WKT si está configurado, 
        # pero lo más fácil es dejar que un trigger o columna calculada lo haga.
        # Si no, subimos el JSON y ejecutamos un SQL final para actualizar geometrías.
        
        try:
            response = requests.post(SUPABASE_URL, headers=headers, json=batch)
            if response.status_code in [200, 201]:
                print(f"Progreso: {i + len(batch)} / {total}")
            else:
                print(f"Error en bloque {i}: {response.text}")
        except Exception as e:
            print(f"Fallo de conexión: {e}")
            time.sleep(2)
            
    print("\n--- ¡SUBIDA COMPLETADA! ---")
    print("Ahora ejecuta este SQL en el panel de Supabase para activar el mapa:")
    print("UPDATE photos SET geometry = ST_SetSRID(ST_MakePoint(lng, lat), 4326) WHERE geometry IS NULL;")

if __name__ == "__main__":
    upload()
