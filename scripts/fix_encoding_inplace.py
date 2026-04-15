"""Corrige mojibake CP850 en la tabla photos con dict de reemplazos."""
import sys
import psycopg2
from psycopg2.extras import execute_batch

sys.stdout.reconfigure(encoding='utf-8')

DB_URL = "postgresql://postgres.ktnavneugmimhdvpnnga:V4BG8aKwXi3qrNn@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"

REPLACEMENTS = {
    '├®': 'é', '├│': 'ó', '├¡': 'í', '├í': 'á', '├▒': 'ñ', '├║': 'ú',
    '├ü': 'Á', '├ô': 'Ó', '├ë': 'É', '├ì': 'Í', '├Ü': 'Ú', '├æ': 'Ñ',
    '├¿': 'è', '├á': 'à', '├╝': 'ü', '├ñ': 'ä', '├º': 'ç', '├ç': 'Ç',
    '├£': 'Ü', '├┤': 'ô', '├╣': 'ù', '├¬': 'ê',
    '├▓': 'ò', '├¼': 'ì', '├»': 'ï', '├Â': 'ö', '├ƒ': 'ß',
    '├ó': 'â', '├Ç': 'À', '├╗': 'û',
}

TEXT_COLS = ['title', 'description', 'era', 'zone', 'author', 'rights', 'source']


def fix_text(s):
    if not isinstance(s, str) or '├' not in s:
        return s
    for k, v in REPLACEMENTS.items():
        if k in s:
            s = s.replace(k, v)
    return s


def main():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cols = ','.join(['id'] + TEXT_COLS)
            cur.execute(f"SELECT {cols} FROM photos;")
            rows = cur.fetchall()
        print(f"Loaded {len(rows)} rows")

        updates = []
        for row in rows:
            pid, *values = row
            fixed = tuple(fix_text(v) for v in values)
            if tuple(fixed) != tuple(values):
                updates.append(tuple(fixed) + (pid,))

        print(f"Rows needing update: {len(updates)}")
        if updates:
            set_clause = ','.join(f"{c}=%s" for c in TEXT_COLS)
            sql = f"UPDATE photos SET {set_clause} WHERE id=%s"
            with conn.cursor() as cur:
                execute_batch(cur, sql, updates, page_size=500)
            conn.commit()
            print(f"Updated {len(updates)} rows")

        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM photos WHERE "
                "title LIKE '%├%' OR description LIKE '%├%'"
            )
            remaining = cur.fetchone()[0]
            print(f"Rows with residual mojibake: {remaining}")
            cur.execute("SELECT id, LEFT(description,150) FROM photos WHERE id=23450;")
            print(f"Sample id=23450: {cur.fetchone()}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
