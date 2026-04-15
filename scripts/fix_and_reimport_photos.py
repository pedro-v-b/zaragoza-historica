import json, sys, psycopg2
from psycopg2.extras import execute_values

sys.stdout.reconfigure(encoding='utf-8')

DB_URL = "postgresql://postgres.ktnavneugmimhdvpnnga:V4BG8aKwXi3qrNn@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
JSON_PATH = "data_for_supabase.json"

TEXT_FIELDS = ['title','description','era','zone','author','rights','source']

def fix_enc(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode('cp437').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s

def main():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        photos = json.load(f)
    print(f"Loaded {len(photos)} photos")

    rows = []
    for p in photos:
        for k in TEXT_FIELDS:
            if k in p and p[k] is not None:
                p[k] = fix_enc(p[k])
        tags = p.get('tags') or []
        if isinstance(tags, list):
            tags = [fix_enc(t) if isinstance(t, str) else t for t in tags]
        rows.append((
            p['id'], p['title'], p['description'], p.get('year'),
            p.get('year_from'), p.get('year_to'), p.get('era'), p.get('zone'),
            p['lat'], p['lng'], p['image_url'], p['thumb_url'],
            p.get('source'), p.get('author'), p.get('rights'), tags
        ))

    print(f"Prepared {len(rows)} rows. Sample fixed title: {rows[0][1]}")
    print(f"Sample fixed desc: {rows[0][2][:120]}")

    conn = psycopg2.connect(DB_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM photos;")
            print(f"Deleted existing rows: {cur.rowcount}")
            execute_values(cur,
                """INSERT INTO photos
                (id,title,description,year,year_from,year_to,era,zone,lat,lng,image_url,thumb_url,source,author,rights,tags)
                VALUES %s""",
                rows, page_size=500)
            cur.execute("SELECT setval('photos_id_seq', (SELECT MAX(id) FROM photos));")
            cur.execute("SELECT COUNT(*) FROM photos;")
            total = cur.fetchone()[0]
        conn.commit()
        print(f"DONE. Total photos in DB: {total}")
    except Exception as e:
        conn.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
