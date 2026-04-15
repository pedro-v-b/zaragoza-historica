import psycopg2
import os

# Configuración
LOCAL_DB = "postgresql://zaragoza_user:zaragoza_pass@127.0.0.1:5432/zaragoza_historica"
REMOTE_DB = "postgresql://postgres:V4BG8aKwXi3qrNn@db.ktnavneugmimhdvpnnga.supabase.co:5432/postgres"

# Prefijo público de Supabase
PUBLIC_URL_PREFIX = "https://ktnavneugmimhdvpnnga.supabase.co/storage/v1/object/public/uploads/"

def migrate_photos():
    local_conn = None
    remote_conn = None
    try:
        print("Conectando con base de datos LOCAL...")
        local_conn = psycopg2.connect(LOCAL_DB)
        local_conn.set_client_encoding('UTF8')
        local_cur = local_conn.cursor()
        
        print("Conectando con SUPABASE...")
        remote_conn = psycopg2.connect(REMOTE_DB)
        remote_conn.set_client_encoding('UTF8')
        remote_conn.autocommit = True
        remote_cur = remote_conn.cursor()
        
        # 1. Obtener todas las fotos de local
        print("Extrayendo registros de local...")
        local_cur.execute("SELECT title, description, year, year_from, year_to, era, zone, lat, lng, image_url, thumb_url, source, author, rights, tags FROM photos")
        rows = local_cur.fetchall()
        print(f"Encontrados {len(rows)} registros.")
        
        # 2. Insertar en remoto con URLs corregidas
        print("Insertando registros en Supabase...")
        
        # Preparar los datos
        migrated_rows = []
        for row in rows:
            # Reemplazar el prefijo local /uploads/ por la URL pública de Supabase
            image_url = row[9].replace('/uploads/', PUBLIC_URL_PREFIX)
            thumb_url = row[10].replace('/uploads/', PUBLIC_URL_PREFIX)
            
            # Reemplazar extensiones si fuera necesario (aunque ya lo hicimos en local)
            image_url = image_url.replace('.jpg', '.webp').replace('.png', '.webp')
            thumb_url = thumb_url.replace('.jpg', '.webp').replace('.png', '.webp')
            
            # Formar la nueva fila
            migrated_rows.append(row[:9] + (image_url, thumb_url) + row[11:])
        
        # Ejecutar inserción masiva
        insert_query = """
        INSERT INTO photos (title, description, year, year_from, year_to, era, zone, lat, lng, image_url, thumb_url, source, author, rights, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Insertar uno a uno para evitar problemas de tamaño de comando, o en bloques
        for i in range(0, len(migrated_rows), 100):
            batch = migrated_rows[i:i+100]
            remote_cur.executemany(insert_query, batch)
            print(f"Procesados: {i + len(batch)} / {len(migrated_rows)}")
            
        print("\n--- ¡MIGRACIÓN DE DATOS COMPLETADA CON ÉXITO! ---")
        
    except Exception as e:
        print(f"ERROR DURANTE LA MIGRACIÓN: {e}")
    finally:
        if local_conn: local_conn.close()
        if remote_conn: remote_conn.close()

if __name__ == "__main__":
    migrate_photos()
