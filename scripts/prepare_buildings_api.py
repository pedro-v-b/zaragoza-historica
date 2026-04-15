import json
import os

# Configuración
SQL_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\buildings_data.sql"

def get_batches(batch_size=500):
    print(f"Leyendo edificios de {SQL_FILE}...")
    # Leer como utf-16 porque fue generado por PowerShell redireccionando
    with open(SQL_FILE, 'r', encoding='utf-16') as f:
        lines = [l for l in f if 'INSERT INTO public.catastro_buildings' in l]
    
    total = len(lines)
    print(f"Total registros: {total}")
    
    for i in range(0, total, batch_size):
        batch = lines[i:i+batch_size]
        sql = "".join(batch).replace("public.catastro_buildings", "catastro_buildings")
        yield sql, i + len(batch), total

if __name__ == "__main__":
    # Generar el primer bloque para probar vía MCP
    gen = get_batches()
    sql, count, total = next(gen)
    with open(r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\buildings_batch.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"Bloque {count}/{total} preparado en buildings_batch.sql")
