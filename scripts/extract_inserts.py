import os

INPUT_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\photos_data_migrated.sql"
OUTPUT_FILE = r"C:\Users\pvial\Desktop\TFG DAM v2\scripts\inserts_only.sql"

def extract():
    try:
        print("Extrayendo INSERTs...")
        with open(INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
                for line in f:
                    if line.strip().startswith('INSERT INTO'):
                        out.write(line)
        print("Extracción completada.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract()
