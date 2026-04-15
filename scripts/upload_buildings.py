import psycopg2
import os
import re

# Configuración
REMOTE_DB = "postgresql://postgres:V4BG8aKwXi3qrNn@65.109.93.223:5432/postgres?connect_timeout=10"
SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\buildings_data.sql"

def upload_buildings():
    conn = None
    try:
        print("Conectando con SUPABASE...")
        conn = psycopg2.connect(REMOTE_DB)
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"Leyendo archivo de edificios: {SQL_FILE}")
        # Leer como utf-16 porque fue generado por PowerShell redireccionando
        with open(SQL_FILE, 'r', encoding='utf-16') as f:
            lines = [l for l in f if 'INSERT INTO public.catastro_buildings' in l]
        
        total = len(lines)
        print(f"Total de edificios a subir: {total}")
        
        batch_size = 200
        for i in range(0, total, batch_size):
            batch = lines[i:i+batch_size]
            batch_sql = "".join(batch)
            
            # Limpiar posibles errores de codificación en el SQL
            batch_sql = batch_sql.replace("public.catastro_buildings", "catastro_buildings")
            
            try:
                cur.execute(batch_sql)
                print(f"Progreso: {i + len(batch)} / {total}")
            except Exception as e_batch:
                print(f"Error en bloque {i}: {e_batch}")
                conn.rollback()
                # Intentar uno a uno si falla el bloque (opcional, pero lento)
                continue
            
        print("\n--- ¡MIGRACIÓN DE EDIFICIOS FINALIZADA! ---")
        
    except Exception as e:
        print(f"Error crítico: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    upload_buildings()
