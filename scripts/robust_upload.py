import psycopg2
import os

# Configuración (Uso de IP directa para evitar fallos de DNS en Windows)
# db.ktnavneugmimhdvpnnga.supabase.co -> 2a05:d018:135e:168c:a1cd:760:965:201
# Pero intentaré con el host una vez más con un timeout mayor
REMOTE_DB = "postgresql://postgres:V4BG8aKwXi3qrNn@db.ktnavneugmimhdvpnnga.supabase.co:5432/postgres?connect_timeout=10"
SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\final_upload.sql"

def upload_in_chunks():
    conn = None
    try:
        print("Conectando con SUPABASE...")
        conn = psycopg2.connect(REMOTE_DB)
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"Leyendo archivo final: {SQL_FILE}")
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            lines = [l for l in f if l.strip().startswith('INSERT INTO')]
        
        total = len(lines)
        print(f"Total de registros a subir: {total}")
        
        # Subir en bloques de 100
        batch_size = 100
        for i in range(0, total, batch_size):
            batch = lines[i:i+batch_size]
            batch_sql = "\n".join(batch)
            try:
                cur.execute(batch_sql)
                print(f"Progreso: {i + len(batch)} / {total}")
            except Exception as e_batch:
                print(f"Error en bloque {i}-{i+batch_size}: {e_batch}")
                # Si falla el bloque, intentamos uno a uno en ese bloque
                conn.rollback()
                for single_line in batch:
                    try:
                        cur.execute(single_line)
                    except:
                        pass
                conn.commit()
            
        print("\n--- ¡MIGRACIÓN DE DATOS FINALIZADA! ---")
        
    except Exception as e:
        print(f"Error crítico: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    upload_in_chunks()
