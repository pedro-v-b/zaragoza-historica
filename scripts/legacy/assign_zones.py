import json
import psycopg2
from shapely.geometry import shape, Point
import os

def main():
    # Configuración DB (según tu docker-compose)
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="zaragoza_historica",
        user="zaragoza_user",
        password="zaragoza_pass"
    )
    cur = conn.cursor()

    # Cargar Barrios desde el GeoJSON del frontend
    geojson_path = r"C:\Users\pvial\Desktop\TFG DAM v2\frontend\public\barrios-zaragoza-wgs84.geojson"
    with open(geojson_path, 'r', encoding='utf-8') as f:
        barrios_data = json.load(f)

    print("Procesando barrios...")
    barrios_geoms = []
    for feature in barrios_data['features']:
        name = feature['properties'].get('name') or feature['properties'].get('JUNTA')
        geom = shape(feature['geometry'])
        barrios_geoms.append((name, geom))

    # Obtener fotos sin zona
    cur.execute("SELECT id, lat, lng FROM photos WHERE zone IS NULL OR zone = '';")
    photos = cur.fetchall()
    print(f"Encontradas {len(photos)} fotos para zonificar.")

    updated = 0
    for photo_id, lat, lng in photos:
        point = Point(lng, lat) # GeoJSON usa Long, Lat
        
        for name, geom in barrios_geoms:
            if geom.contains(point):
                cur.execute("UPDATE photos SET zone = %s WHERE id = %s", (name, photo_id))
                updated += 1
                break
        
        if updated % 500 == 0 and updated > 0:
            print(f"Actualizadas {updated} fotos...")

    conn.commit()
    cur.close()
    conn.close()
    print(f"¡Hecho! Se han asignado {updated} fotos a sus respectivos barrios.")

if __name__ == "__main__":
    main()
