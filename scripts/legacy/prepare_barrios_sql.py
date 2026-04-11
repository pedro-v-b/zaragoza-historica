import json

def main():
    geojson_path = r"C:\Users\pvial\Desktop\TFG DAM v2\frontend\public\barrios-zaragoza-wgs84.geojson"
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open('barrios_import.sql', 'w', encoding='utf-8') as f:
        f.write("CREATE TABLE IF NOT EXISTS barrios (id serial primary key, name varchar(255), geom geometry(Geometry, 4326));\n")
        f.write("DELETE FROM barrios;\n")
        
        for feature in data['features']:
            name = feature['properties'].get('name') or feature['properties'].get('JUNTA')
            # Escapar comillas simples en el nombre
            name = name.replace("'", "''")
            geom = json.dumps(feature['geometry'])
            f.write(f"INSERT INTO barrios (name, geom) VALUES ('{name}', ST_GeomFromGeoJSON('{geom}'));\n")
        
        f.write("\n-- Actualizar las fotos con el nombre del barrio\n")
        f.write("UPDATE photos SET zone = barrios.name FROM barrios WHERE ST_Contains(barrios.geom, photos.geometry);\n")
        f.write("DROP TABLE barrios;\n")

if __name__ == "__main__":
    main()
