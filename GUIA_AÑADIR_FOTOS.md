# 📍 Guía Completa: Añadir Fotos Geolocalizadas

## 🎯 Métodos Disponibles

### Método 1: Script Python Interactivo (⭐ Recomendado)
### Método 2: Editar SQL manualmente
### Método 3: GUI con pgAdmin
### Método 4: API REST (futuro)

---

## 📋 MÉTODO 1: Script Python Interactivo

### Paso 1: Ejecutar el script
```powershell
cd "C:\Users\pvial\Desktop\TFG DAM"
python add_photo.py
```

### Paso 2: Responder las preguntas
El script te preguntará:
- ✏️ Título de la foto
- 📄 Descripción
- 📅 Año (exacto o rango)
- 🕰️ Época (se sugiere automáticamente)
- 📍 Zona de Zaragoza
- 🗺️ Coordenadas (copiar desde Google Maps)
- 🖼️ Nombre del archivo
- 📚 Fuente, autor, derechos
- 🏷️ Tags (etiquetas)

### Paso 3: El script genera automáticamente:
- ✅ Código SQL válido
- ✅ Guardado en `mis_fotos.sql`
- ✅ Listo para ejecutar

### Paso 4: Preparar las imágenes

**Importante**: Las imágenes deben estar en estas carpetas:

```
backend/
  uploads/
    foto1.jpg          ← Imagen completa (recomendado: max 1920x1080)
    foto2.jpg
    thumbs/
      foto1.jpg        ← Miniatura (recomendado: 300x200)
      foto2.jpg
```

**Consejos para las imágenes:**
- Formato: JPG o PNG
- Imagen completa: máximo 1920x1080 px (para carga rápida)
- Miniatura: 300x200 px o similar
- Usa nombres sin espacios ni tildes: `plaza_pilar_1945.jpg`

### Paso 5: Ejecutar el SQL generado

```powershell
# Desde el directorio raíz del proyecto
docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < mis_fotos.sql
```

### Paso 6: Verificar en el navegador
Recarga la página: http://localhost:5173/

---

## 📋 MÉTODO 2: Editar SQL Manualmente

### Paso 1: Crear tu archivo SQL

Usa la plantilla en: `backend/database/PLANTILLA_NUEVAS_FOTOS.sql`

### Paso 2: Obtener coordenadas desde Google Maps

1. Ve a **Google Maps**: https://www.google.com/maps/@41.6488,-0.8891,15z
2. Busca el lugar de Zaragoza donde se tomó la foto
3. **Click derecho** en el punto exacto
4. Click en las **coordenadas** que aparecen (primer elemento del menú)
5. Se copian automáticamente: `41.656648, -0.878611`

**Ejemplo visual:**
```
Google Maps → Click derecho → "41.656648, -0.878611"
                              ↑ Click aquí
```

### Paso 3: Rellenar la plantilla

```sql
INSERT INTO photos (
    title, description, year, year_from, year_to, era, zone,
    lat, lng, image_url, thumb_url, source, author, rights, tags
) VALUES (
    'Plaza del Pilar en 1950',
    'Vista panorámica con la Basílica al fondo',
    1950,          -- Año exacto
    NULL,          -- O usa year_from si es aproximado
    NULL,          -- O usa year_to si es aproximado
    'Años 50',
    'Centro',
    41.656648,     -- ← Pega aquí LAT de Google Maps
    -0.878611,     -- ← Pega aquí LNG de Google Maps
    '/uploads/plaza_pilar_1950.jpg',
    '/uploads/thumbs/plaza_pilar_1950.jpg',
    'Archivo Municipal',
    'Juan Pérez',
    'Dominio público',
    ARRAY['Plaza del Pilar', 'Basílica', 'histórico']
);
```

### Paso 4: Guardar y ejecutar

```powershell
# Guarda tu archivo como: mis_nuevas_fotos.sql
# Luego ejecútalo:
docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < backend\database\mis_nuevas_fotos.sql
```

---

## 📋 MÉTODO 3: Usando pgAdmin (GUI)

### Paso 1: Instalar pgAdmin (opcional)
- Descarga: https://www.pgadmin.org/download/

### Paso 2: Conectar a la base de datos
- Host: `localhost`
- Puerto: `5432`
- Database: `zaragoza_historica`
- Usuario: `zaragoza_user`
- Password: `zaragoza_pass`

### Paso 3: Insertar datos con formulario
1. Navega a: `Databases` → `zaragoza_historica` → `Schemas` → `public` → `Tables` → `photos`
2. Click derecho → `View/Edit Data` → `All Rows`
3. Click en el botón `+` para añadir nueva fila
4. Rellena los campos (las coordenadas como números decimales)
5. Click en `Save`

---

## 🗺️ Guía de Coordenadas de Zaragoza

### Lugares emblemáticos con sus coordenadas:

| Lugar | Latitud | Longitud | Zona |
|-------|---------|----------|------|
| Plaza del Pilar | 41.656648 | -0.878611 | Centro |
| Puente de Piedra | 41.659168 | -0.878333 | Casco Histórico |
| Mercado Central | 41.657932 | -0.879471 | Centro |
| Paseo Independencia | 41.654321 | -0.880123 | Centro |
| Estación del Norte | 41.665432 | -0.893210 | Delicias |
| Parque Grande | 41.642567 | -0.891234 | Universidad |
| Universidad | 41.646789 | -0.896543 | Universidad |
| Aljafería | 41.655987 | -0.897654 | San José |
| Plaza España | 41.652345 | -0.885432 | Centro |
| Basílica del Pilar | 41.657234 | -0.878765 | Casco Histórico |

### Zonas de Zaragoza (para el campo `zone`):

- **Centro**: Paseo Independencia, Plaza España, Don Jaime
- **Casco Histórico**: El Tubo, Plaza del Pilar, La Seo
- **Delicias**: Estación Delicias, Parque Delicias
- **Universidad**: Campus, Paraninfo, Parque Grande
- **Actur**: Barrio Actur, Canal Imperial
- **San José**: Aljafería, Parque Tío Jorge
- **Torrero**: Venecia, Parque Primo de Rivera
- **Oliver**: Barrio Oliver
- **Las Fuentes**: Mercado Las Fuentes
- **Arrabal**: Barrio del Arrabal

### Épocas disponibles (campo `era`):

- `Años 20` (1920-1929)
- `Años 30` (1930-1939)
- `Años 40` (1940-1949)
- `Años 50` (1950-1959)
- `Años 60` (1960-1969)
- `Años 70` (1970-1979)
- `Años 80` (1980-1989) - Añadir si necesitas

---

## 🖼️ Preparación de Imágenes

### Opción A: Usando herramientas online

**Para redimensionar/optimizar:**
- https://squoosh.app/ (Google, gratis, sin registro)
- https://tinypng.com/ (compresión PNG/JPG)
- https://imageresizer.com/ (redimensionar rápido)

**Recomendaciones:**
```
Imagen completa:
  - Ancho: 1200-1920 px
  - Formato: JPG calidad 80%
  - Peso: < 500 KB

Miniatura (thumb):
  - Ancho: 300 px
  - Formato: JPG calidad 75%
  - Peso: < 50 KB
```

### Opción B: Usando Python (automatizado)

Crea este script `resize_images.py`:

```python
from PIL import Image
import os

def resize_image(input_path, output_path, width):
    img = Image.open(input_path)
    ratio = width / img.width
    height = int(img.height * ratio)
    resized = img.resize((width, height), Image.Resampling.LANCZOS)
    resized.save(output_path, 'JPEG', quality=85)

# Uso:
resize_image('original.jpg', 'backend/uploads/foto.jpg', 1920)
resize_image('original.jpg', 'backend/uploads/thumbs/foto.jpg', 300)
```

---

## 🔄 Workflow Recomendado

### Para añadir 1-5 fotos: Método Script Python

```powershell
# 1. Ejecutar script
python add_photo.py

# 2. Copiar imágenes
copy "C:\mis_fotos\foto.jpg" "backend\uploads\foto.jpg"
copy "C:\mis_fotos\foto_thumb.jpg" "backend\uploads\thumbs\foto.jpg"

# 3. Ejecutar SQL generado
docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < mis_fotos.sql

# 4. Verificar
Invoke-RestMethod "http://localhost:3000/api/photos?page=1&pageSize=50" | ConvertTo-Json -Depth 5
```

### Para añadir 6+ fotos: Método SQL manual

1. Crea un archivo `lote_fotos.sql`
2. Copia múltiples INSERT (usa la plantilla)
3. Prepara todas las imágenes en `backend/uploads/`
4. Ejecuta todo de una vez:
```powershell
docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < lote_fotos.sql
```

---

## ✅ Verificación

### Comprobar que se añadió correctamente:

```powershell
# Ver total de fotos
$response = Invoke-RestMethod "http://localhost:3000/api/photos?page=1&pageSize=1"
Write-Host "Total de fotos: $($response.total)"

# Ver últimas 3 fotos añadidas
$response = Invoke-RestMethod "http://localhost:3000/api/photos?page=1&pageSize=3"
$response.data | Select-Object id, title, year, zone | Format-Table

# Buscar una foto específica
$response = Invoke-RestMethod "http://localhost:3000/api/photos?q=Plaza+del+Pilar"
$response.data | Select-Object title, year | Format-Table
```

### En la web:
1. Ve a http://localhost:5173/
2. Deberías ver el nuevo marcador en el mapa
3. Aplica filtros para encontrarla
4. Click en el marcador → debería mostrar popup con imagen

---

## 🐛 Problemas Comunes

### ❌ Error: "relation 'photos' does not exist"
```powershell
# Ejecuta primero el schema
docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < backend\database\schema.sql
```

### ❌ Imagen no se ve (broken image)
- Verifica que el archivo existe en `backend/uploads/`
- Verifica que el nombre coincide exactamente (case-sensitive)
- Revisa permisos del archivo

### ❌ Coordenadas incorrectas (foto en el mar/otro país)
- Verifica orden: **LAT primero, LNG segundo**
- Google Maps: `41.656648, -0.878611`
  - ✅ lat=41.656648, lng=-0.878611
  - ❌ lat=-0.878611, lng=41.656648 (incorrecto!)

### ❌ Error SQL: syntax error
- Verifica comillas simples en textos con apóstrofes
- Ejemplo: `'L'Aljafería'` → Error
- Solución: `'L''Aljafería'` o `'La Aljafería'`

---

## 📊 Ejemplo Completo Paso a Paso

### Escenario: Añadir foto de "Torre del Pilar 1960"

**1. Obtener coordenadas:**
- Google Maps → busca "Torre del Pilar Zaragoza"
- Click derecho → coordenadas: `41.657234, -0.878765`

**2. Preparar imagen:**
```powershell
# Copiar y redimensionar (si tienes la foto)
copy "C:\fotos_zaragoza\torre_pilar.jpg" "backend\uploads\torre_pilar_1960.jpg"
copy "C:\fotos_zaragoza\torre_pilar_thumb.jpg" "backend\uploads\thumbs\torre_pilar_1960.jpg"
```

**3. Crear SQL:**
```sql
INSERT INTO photos (
    title, description, year, year_from, year_to, era, zone,
    lat, lng, image_url, thumb_url, source, author, rights, tags
) VALUES (
    'Torre del Pilar en 1960',
    'Vista de la Torre del Pilar desde el Ebro',
    1960, NULL, NULL,
    'Años 60',
    'Casco Histórico',
    41.657234,
    -0.878765,
    '/uploads/torre_pilar_1960.jpg',
    '/uploads/thumbs/torre_pilar_1960.jpg',
    'Archivo Histórico Provincial',
    'José García',
    'Dominio público',
    ARRAY['Torre del Pilar', 'Basílica', 'arquitectura']
);
```

**4. Ejecutar:**
```powershell
# Guardar SQL en archivo
Set-Content -Path "nueva_foto.sql" -Value "INSERT INTO photos..."

# Ejecutar
docker exec -i zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica < nueva_foto.sql
```

**5. Verificar:**
- http://localhost:5173/
- Buscar "Torre del Pilar"
- Debería aparecer en el mapa y en la lista

---

## 🚀 Próximos Pasos

Una vez tengas varias fotos:
1. ✅ Prueba los filtros (por año, zona, época)
2. ✅ Verifica la sincronización mapa-lista
3. ✅ Captura screenshots para tu TFG
4. ✅ Documenta tus fuentes históricas

---

## 📚 Recursos Útiles

### Para encontrar fotos históricas de Zaragoza:
- **Archivo Municipal de Zaragoza**: https://www.zaragoza.es/sede/portal/datos-abiertos/
- **Europeana**: https://www.europeana.eu/
- **Biblioteca Nacional**: http://www.bne.es/
- **Memoria de Aragón**: https://memoriadearagon.es/

### Para coordenadas:
- **Google Maps**: https://www.google.com/maps/@41.6488,-0.8891,15z
- **OpenStreetMap**: https://www.openstreetmap.org/#map=14/41.6488/-0.8891

---

**¿Tienes dudas?** Consulta `PLANTILLA_NUEVAS_FOTOS.sql` para ejemplos completos.
