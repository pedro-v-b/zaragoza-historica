"""Convierte thumbs JPG -> WebP en memoria y los sube a Supabase Storage."""
import io
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_REF = "ktnavneugmimhdvpnnga"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0bmF2bmV1Z21pbWhkdnBubmdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4OTg2NDIsImV4cCI6MjA5MTQ3NDY0Mn0.-opoLYwAWnDirmIK3mSektMBFBjzL584VqJE8eIlBKc"
BUCKET = "uploads"
BASE_URL = f"https://{PROJECT_REF}.supabase.co/storage/v1/object/{BUCKET}"
THUMBS_DIR = Path(r"C:\Users\pvial\Desktop\TFG DAM v2\uploads\thumbs")

HEADERS = {
    "Authorization": f"Bearer {ANON_KEY}",
    "apikey": ANON_KEY,
    "Content-Type": "image/webp",
    "x-upsert": "true",
}


def process_one(jpg_path: Path):
    name = jpg_path.stem + ".webp"
    url = f"{BASE_URL}/thumbs/{name}"
    try:
        img = Image.open(jpg_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=85, method=4)
        data = buf.getvalue()
        with httpx.Client(timeout=30.0) as c:
            r = c.post(url, headers=HEADERS, content=data)
        if r.status_code in (200, 201):
            return "ok", len(data)
        return f"err{r.status_code}", 0
    except Exception as e:
        return f"exc:{type(e).__name__}", 0


def main():
    files = sorted(THUMBS_DIR.glob("*.jpg"))
    total = len(files)
    print(f"[*] {total} thumbs .jpg a procesar")
    t0 = time.perf_counter()
    ok = 0
    errors = 0
    bytes_sent = 0
    with ThreadPoolExecutor(max_workers=24) as ex:
        futs = {ex.submit(process_one, f): f for f in files}
        for i, fut in enumerate(as_completed(futs), 1):
            status, size = fut.result()
            if status == "ok":
                ok += 1
                bytes_sent += size
            else:
                errors += 1
                if errors <= 5:
                    print(f"  [WARN] {futs[fut].name}: {status}")
            if i % 250 == 0 or i == total:
                elapsed = time.perf_counter() - t0
                rate = i / elapsed if elapsed else 0
                mb = bytes_sent / 1_048_576
                print(f"  {i}/{total}  ok={ok} err={errors}  {mb:.1f}MB  {rate:.1f}/s  {elapsed:.0f}s")
    print(f"\nDONE. ok={ok} err={errors} total_mb={bytes_sent/1_048_576:.1f} in {time.perf_counter()-t0:.0f}s")


if __name__ == "__main__":
    main()
