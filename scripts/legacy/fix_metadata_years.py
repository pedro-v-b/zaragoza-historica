import json
import re
from pathlib import Path

METADATA_FILE = Path(r"C:\Users\pvial\flickr_scraper\metadata.json")

def roman_to_int(roman):
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(roman)):
        if i > 0 and rom_val[roman[i]] > rom_val[roman[i - 1]]:
            int_val += rom_val[roman[i]] - 2 * rom_val[roman[i - 1]]
        else:
            int_val += rom_val[roman[i]]
    return int_val

def extract_precise_year(title):
    if not title: return None, None, None
    
    # 1. Buscar años de 4 dígitos específicos: "1328", "1950"
    # Buscamos números entre 1000 y 2025 que no estén precedidos por 's.' o 'siglo'
    year_match = re.search(r'(?<!s\.\s)(?<!siglo\s)\b(1\d{3}|20[0-2]\d)\b', title)
    if year_match:
        y = int(year_match.group(1))
        return y, y, y

    # 2. Buscar siglos: "s. XIII", "siglo XIV", "s. XX"
    siglo_match = re.search(r'(?:s\.|siglo)\s+([IVXLCDM]+)', title, re.IGNORECASE)
    if siglo_match:
        siglo_romano = siglo_match.group(1).upper()
        try:
            siglo = roman_to_int(siglo_romano)
            y_start = (siglo - 1) * 100
            y_end = y_start + 99
            return y_start + 50, y_start, y_end
        except: pass

    # 3. Buscar décadas: "años 20", "años 50"
    # Asumimos siglo XX para "años 20" si no se especifica, pero GAZA suele ser siglo XX
    decade_match = re.search(r'años (\d{2})', title, re.IGNORECASE)
    if decade_match:
        d = int(decade_match.group(1))
        y_start = 1900 + d if d > 20 else 2000 + d # 20 -> 1920, 10 -> 2010? GAZA es más 1900
        if d > 25: y_start = 1900 + d
        else: y_start = 1900 + d # Por simplicidad en GAZA casi todo es 19xx
        return y_start, y_start, y_start + 9

    return None, None, None

def main():
    print(f"Cargando {METADATA_FILE}...")
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed_count = 0
    for item in data:
        y, y_from, y_to = extract_precise_year(item.get('title', ''))
        if y:
            item['capture_year'] = y
            item['year_from'] = y_from
            item['year_to'] = y_to
            fixed_count += 1
        else:
            # Si no hay en el título, mantenemos lo que había o marcamos como nulo para que import lo maneje
            item['capture_year'] = None 
            
    print(f"Años extraídos con precisión en {fixed_count} fotos.")
    
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Archivo metadata.json actualizado.")

if __name__ == "__main__":
    main()
