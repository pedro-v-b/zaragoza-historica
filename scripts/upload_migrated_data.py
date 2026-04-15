import psycopg2
import os

# Configuración
REMOTE_DB = "postgresql://postgres:V4BG8aKwXi3qrNn@db.ktnavneugmimhdvpnnga.supabase.co:5432/postgres"
SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\photos_data_migrated.sql"

def upload_data():
    conn = None
    try:
        print("Conectando con SUPABASE...")
        conn = psycopg2.connect(REMOTE_DB)
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"Leyendo archivo migrado: {SQL_FILE}")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filtrar solo las líneas que son INSERTs
        insert_lines = [line for line in lines if line.strip().startswith('INSERT INTO')]
        total = len(insert_lines)
        print(f"Total de registros a subir: {total}")
        
        # Subir en bloques de 50 para seguridad
        for i in range(0, total, 50):
            batch = insert_lines[i:i+50]
            batch_sql = "\n".join(batch)
            cur.execute(batch_sql)
            print(f"Progreso: {i + len(batch)} / {total}")
            
        print("\n--- ¡DATOS SUBIDOS A SUPABASE CON ÉXITO! ---")
        
    except Exception as e:
        print(f"Error al subir datos: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    upload_data()
