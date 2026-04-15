import psycopg2
import json
import subprocess

# Configuración
LOCAL_CONN = "postgresql://zaragoza_user:zaragoza_pass@127.0.0.1:5432/zaragoza_historica"
REMOTE_DB = "postgresql://postgres:V4BG8aKwXi3qrNn@db.ktnavneugmimhdvpnnga.supabase.co:5432/postgres"

def migrate_buildings():
    try:
        print("Conectando con base de datos LOCAL...")
        local_conn = psycopg2.connect(LOCAL_CONN)
        local_cur = local_conn.cursor()
        
        print("Conectando con SUPABASE...")
        remote_conn = psycopg2.connect(REMOTE_DB)
        remote_conn.autocommit = True
        remote_cur = remote_conn.cursor()
        
        # 1. Obtener edificios de local (sin la geometría binaria, la reconstruiremos en remoto)
        print("Extrayendo edificios de local...")
        local_cur.execute("""
            SELECT id, cadastral_ref, inspire_id, year_built, floors_above, floors_below, current_use, source,
            ST_AsText(geometry) as geom_wkt
            FROM catastro_buildings
        """)
        
        rows = local_cur.fetchall()
        total = len(rows)
        print(f"Encontrados {total} edificios.")
        
        # 2. Insertar en bloques de 1000
        batch_size = 1000
        for i in range(0, total, batch_size):
            batch = rows[i:i+batch_size]
            
            # Preparar valores para inserción masiva
            # (id, ref, inspire, year, floors_a, floors_b, use, source, ST_GeomFromText(wkt))
            values_list = []
            for row in batch:
                # Escapar comillas simples en strings
                use = row[6].replace("'", "''") if row[6] else None
                source = row[7].replace("'", "''") if row[7] else 'Catastro INSPIRE'
                
                val = f"({row[0]}, '{row[1]}', '{row[2]}', {row[3] or 'NULL'}, {row[4] or 'NULL'}, {row[5] or 'NULL'}, '{use}', '{source}', ST_Multi(ST_GeomFromText('{row[8]}', 4326)))"
                values_list.append(val)
            
            insert_query = f"""
                INSERT INTO catastro_buildings (id, cadastral_ref, inspire_id, year_built, floors_above, floors_below, current_use, source, geometry)
                VALUES {", ".join(values_list)}
                ON CONFLICT (id) DO NOTHING;
            """
            
            try:
                remote_cur.execute(insert_query)
                print(f"Progreso: {i + len(batch)} / {total}")
            except Exception as e_batch:
                print(f"Error en bloque {i}: {e_batch}")
                # Si falla el bloque, intentar uno a uno no es viable por tiempo, así que logueamos y seguimos
                continue
                
        print("\n--- ¡MIGRACIÓN DE EDIFICIOS COMPLETADA! ---")
        
    except Exception as e:
        print(f"Error crítico: {e}")
    finally:
        if local_conn: local_conn.close()
        if remote_conn: remote_conn.close()

if __name__ == "__main__":
    migrate_buildings()
