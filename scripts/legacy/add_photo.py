#!/usr/bin/env python3
"""
Script para generar INSERTs SQL de fotos geolocalizadas
Uso: python add_photo.py
"""

import sys

def get_input(prompt, default=None):
    """Obtener input del usuario con valor por defecto"""
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    return input(f"{prompt}: ").strip()

def get_coordinates():
    """Obtener coordenadas desde Google Maps"""
    print("\n📍 OBTENER COORDENADAS:")
    print("1. Ve a Google Maps: https://www.google.com/maps/@41.6488,-0.8891,15z")
    print("2. Click derecho en el punto exacto donde se tomó la foto")
    print("3. Click en las coordenadas que aparecen")
    print("4. Se copiarán en formato: 41.656648, -0.878611")
    print("5. Pégalas aquí abajo\n")
    
    coords = input("Pega las coordenadas (lat, lng): ").strip()
    try:
        lat, lng = [x.strip() for x in coords.split(',')]
        return float(lat), float(lng)
    except:
        print("❌ Error: formato incorrecto. Usa: latitud, longitud")
        return get_coordinates()

def main():
    print("=" * 60)
    print("🗺️  AÑADIR NUEVA FOTO GEOLOCALIZADA")
    print("=" * 60)
    
    # Datos básicos
    title = get_input("\n📝 Título de la foto")
    description = get_input("📄 Descripción detallada")
    
    # Año
    print("\n📅 FECHA:")
    print("  Opción 1: Año exacto (ej: 1950)")
    print("  Opción 2: Rango de años (ej: 1945-1955)")
    year_type = get_input("¿Año exacto o rango? (exacto/rango)", "exacto")
    
    if year_type.lower().startswith('r'):
        year_from = int(get_input("Año desde"))
        year_to = int(get_input("Año hasta"))
        year = "NULL"
        era_year = year_from
    else:
        year = int(get_input("Año"))
        year_from = "NULL"
        year_to = "NULL"
        era_year = year
    
    # Determinar época automáticamente
    if era_year < 1930:
        era_default = "Años 20"
    elif era_year < 1940:
        era_default = "Años 30"
    elif era_year < 1950:
        era_default = "Años 40"
    elif era_year < 1960:
        era_default = "Años 50"
    elif era_year < 1970:
        era_default = "Años 60"
    else:
        era_default = "Años 70"
    
    era = get_input(f"🕰️  Época", era_default)
    
    # Zona
    print("\n📍 ZONA:")
    print("  Opciones: Centro, Casco Histórico, Delicias, Universidad, Actur")
    print("  San José, Torrero, Oliver, Las Fuentes, Arrabal")
    zone = get_input("Zona", "Centro")
    
    # Coordenadas
    lat, lng = get_coordinates()
    
    # Archivos
    print("\n🖼️  ARCHIVOS DE IMAGEN:")
    print("  Las imágenes deben estar en:")
    print("  - Completa: backend/uploads/nombre.jpg")
    print("  - Miniatura: backend/uploads/thumbs/nombre.jpg")
    
    filename = get_input("Nombre del archivo (sin ruta)", "foto.jpg")
    image_url = f"/uploads/{filename}"
    thumb_url = f"/uploads/thumbs/{filename}"
    
    # Metadatos
    source = get_input("\n📚 Fuente", "Archivo Municipal de Zaragoza")
    author = get_input("👤 Autor/Fotógrafo", "Desconocido")
    rights = get_input("©️  Derechos", "Dominio público")
    
    # Tags
    print("\n🏷️  TAGS (etiquetas):")
    print("  Separa con comas: Plaza del Pilar, tranvía, histórico")
    tags_input = get_input("Tags")
    tags_list = [f"'{tag.strip()}'" for tag in tags_input.split(',') if tag.strip()]
    tags = f"ARRAY[{', '.join(tags_list)}]"
    
    # Generar SQL
    sql = f"""
-- {title}
INSERT INTO photos (
    title, description, year, year_from, year_to, era, zone,
    lat, lng, image_url, thumb_url, source, author, rights, tags
) VALUES (
    '{title}',
    '{description}',
    {year},
    {year_from},
    {year_to},
    '{era}',
    '{zone}',
    {lat},
    {lng},
    '{image_url}',
    '{thumb_url}',
    '{source}',
    '{author}',
    '{rights}',
    {tags}
);
"""
    
    # Guardar en archivo
    with open('mis_fotos.sql', 'a', encoding='utf-8') as f:
        f.write(sql + "\n")
    
    print("\n" + "=" * 60)
    print("✅ SQL GENERADO:")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    print(f"📁 Guardado en: mis_fotos.sql")
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Copia las imágenes a:")
    print(f"   - backend/uploads/{filename}")
    print(f"   - backend/uploads/thumbs/{filename}")
    print("2. Ejecuta el SQL:")
    print("   docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < mis_fotos.sql")
    print("3. Recarga la página web")
    print("=" * 60)
    
    # ¿Otra foto?
    otra = get_input("\n¿Añadir otra foto? (s/n)", "n")
    if otra.lower() == 's':
        print("\n" * 2)
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado por el usuario")
        sys.exit(0)
