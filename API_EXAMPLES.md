# 📡 Ejemplos de uso de la API - Zaragoza Histórica

Esta guía contiene ejemplos prácticos de todas las llamadas a la API REST.

---

## 🏥 Health Check

### Verificar que el backend está funcionando

```bash
curl http://localhost:3000/api/health
```

**Respuesta**:
```json
{
  "status": "ok",
  "timestamp": "2026-01-19T15:30:00.000Z"
}
```

---

## 📸 Fotos - Listado y filtros

### 1. Obtener todas las fotos (sin filtros)

```bash
curl http://localhost:3000/api/photos
```

**Respuesta**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Plaza del Pilar con el Tranvía",
      "description": "Vista de la Plaza del Pilar...",
      "year": 1935,
      "year_from": 1930,
      "year_to": 1940,
      "era": "Años 30",
      "zone": "Casco Histórico",
      "lat": 41.656648,
      "lng": -0.878611,
      "image_url": "/uploads/plaza-pilar-1935.jpg",
      "thumb_url": "/uploads/thumbs/plaza-pilar-1935.jpg",
      "source": "Archivo Municipal de Zaragoza",
      "author": "Fotógrafo desconocido",
      "rights": "Dominio público",
      "tags": ["Plaza del Pilar", "tranvía", "Basílica", "transporte"],
      "created_at": "2026-01-19T14:00:00.000Z",
      "updated_at": "2026-01-19T14:00:00.000Z"
    },
    // ... más fotos
  ],
  "total": 8,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1
}
```

---

### 2. Filtrar por rango de años

```bash
# Fotos entre 1930 y 1960
curl "http://localhost:3000/api/photos?yearFrom=1930&yearTo=1960"
```

---

### 3. Filtrar por época

```bash
# Solo fotos de los años 50
curl "http://localhost:3000/api/photos?era=Años%2050"
```

**Nota**: `%20` = espacio, `%C3%B1` = ñ (URL encoded)

---

### 4. Filtrar por zona

```bash
# Solo fotos del Casco Histórico
curl "http://localhost:3000/api/photos?zone=Casco%20Histórico"

# Fotos del Centro
curl "http://localhost:3000/api/photos?zone=Centro"
```

---

### 5. Filtrar por bounding box (área visible del mapa)

```bash
# Fotos dentro del rectángulo geográfico
# Formato: minLng,minLat,maxLng,maxLat
curl "http://localhost:3000/api/photos?bbox=-0.9,41.6,-0.8,41.7"
```

**Explicación**:
- `-0.9` = longitud mínima (oeste)
- `41.6` = latitud mínima (sur)
- `-0.8` = longitud máxima (este)
- `41.7` = latitud máxima (norte)

---

### 6. Búsqueda de texto

```bash
# Buscar "tranvía" en título, descripción o tags
curl "http://localhost:3000/api/photos?q=tranvía"

# Buscar "Plaza"
curl "http://localhost:3000/api/photos?q=Plaza"
```

---

### 7. Paginación

```bash
# Primera página (20 resultados)
curl "http://localhost:3000/api/photos?page=1&pageSize=20"

# Segunda página (10 resultados por página)
curl "http://localhost:3000/api/photos?page=2&pageSize=10"
```

---

### 8. Combinar múltiples filtros

```bash
# Fotos del Casco Histórico entre 1930-1960, solo en bbox, paginadas
curl "http://localhost:3000/api/photos?zone=Casco%20Histórico&yearFrom=1930&yearTo=1960&bbox=-0.88,41.65,-0.87,41.66&page=1&pageSize=10"
```

---

## 🔍 Detalle de foto por ID

```bash
curl http://localhost:3000/api/photos/1
```

**Respuesta**:
```json
{
  "id": 1,
  "title": "Plaza del Pilar con el Tranvía",
  "description": "Vista de la Plaza del Pilar con el antiguo tranvía...",
  "year": 1935,
  "year_from": 1930,
  "year_to": 1940,
  "era": "Años 30",
  "zone": "Casco Histórico",
  "lat": 41.656648,
  "lng": -0.878611,
  "image_url": "/uploads/plaza-pilar-1935.jpg",
  "thumb_url": "/uploads/thumbs/plaza-pilar-1935.jpg",
  "source": "Archivo Municipal de Zaragoza",
  "author": "Fotógrafo desconocido",
  "rights": "Dominio público",
  "tags": ["Plaza del Pilar", "tranvía", "Basílica", "transporte"],
  "created_at": "2026-01-19T14:00:00.000Z",
  "updated_at": "2026-01-19T14:00:00.000Z"
}
```

**Error si no existe**:
```json
{
  "error": "Foto no encontrada"
}
```

---

## 📊 Metadatos para filtros

### Obtener épocas, zonas y rango de años disponibles

```bash
curl http://localhost:3000/api/photos/metadata/filters
```

**Respuesta**:
```json
{
  "eras": [
    "Años 20",
    "Años 30",
    "Años 40",
    "Años 50",
    "Años 60",
    "Años 70"
  ],
  "zones": [
    "Casco Histórico",
    "Centro",
    "Delicias",
    "Parque Grande",
    "Romareda",
    "Universidad"
  ],
  "yearRange": {
    "min": 1928,
    "max": 1975
  }
}
```

**Uso**: Para construir los selectores de filtros dinámicamente en el frontend.

---

## 🗺️ Capas del mapa

### Obtener todas las capas disponibles

```bash
curl http://localhost:3000/api/layers
```

**Respuesta**:
```json
[
  {
    "id": 1,
    "name": "Mapa Actual",
    "year": null,
    "type": "current",
    "tile_url_template": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    "attribution": "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors",
    "min_zoom": 10,
    "max_zoom": 19,
    "is_active": true,
    "display_order": 1
  },
  {
    "id": 2,
    "name": "Plano histórico 1935",
    "year": 1935,
    "type": "plan",
    "tile_url_template": null,
    "attribution": "Plano histórico - Archivo Municipal Zaragoza",
    "min_zoom": 12,
    "max_zoom": 17,
    "is_active": true,
    "display_order": 2
  },
  {
    "id": 3,
    "name": "Ortofoto histórica 1960",
    "year": 1960,
    "type": "ortho",
    "tile_url_template": null,
    "attribution": "Ortofoto histórica - CNIG/IGN",
    "min_zoom": 12,
    "max_zoom": 18,
    "is_active": true,
    "display_order": 3
  }
]
```

**Nota**: Capas con `tile_url_template: null` son placeholders para futuro.

---

### Obtener una capa específica

```bash
curl http://localhost:3000/api/layers/1
```

---

## 🧪 Ejemplos con JavaScript (fetch)

### Desde el frontend o Node.js:

```javascript
// 1. Health check
const health = await fetch('http://localhost:3000/api/health');
const status = await health.json();
console.log(status); // { status: 'ok', timestamp: '...' }

// 2. Obtener fotos con filtros
const params = new URLSearchParams({
  yearFrom: '1930',
  yearTo: '1960',
  era: 'Años 50',
  page: '1',
  pageSize: '10'
});

const response = await fetch(`http://localhost:3000/api/photos?${params}`);
const data = await response.json();
console.log(data.items); // Array de fotos
console.log(data.total); // Total de resultados

// 3. Obtener foto por ID
const photo = await fetch('http://localhost:3000/api/photos/1');
const photoData = await photo.json();
console.log(photoData.title);

// 4. Obtener metadatos
const meta = await fetch('http://localhost:3000/api/photos/metadata/filters');
const metadata = await meta.json();
console.log(metadata.eras); // ['Años 30', 'Años 50', ...]
console.log(metadata.zones); // ['Casco Histórico', 'Centro', ...]
console.log(metadata.yearRange); // { min: 1928, max: 1975 }

// 5. Obtener capas
const layers = await fetch('http://localhost:3000/api/layers');
const layersData = await layers.json();
console.log(layersData); // Array de capas
```

---

## 🐍 Ejemplos con Python (requests)

```python
import requests

BASE_URL = 'http://localhost:3000/api'

# 1. Health check
response = requests.get(f'{BASE_URL}/health')
print(response.json())  # {'status': 'ok', 'timestamp': '...'}

# 2. Obtener fotos con filtros
params = {
    'yearFrom': 1930,
    'yearTo': 1960,
    'era': 'Años 50',
    'zone': 'Centro',
    'page': 1,
    'pageSize': 10
}
response = requests.get(f'{BASE_URL}/photos', params=params)
data = response.json()
print(f"Total fotos: {data['total']}")
for photo in data['items']:
    print(f"- {photo['title']} ({photo['year']})")

# 3. Obtener foto por ID
response = requests.get(f'{BASE_URL}/photos/1')
photo = response.json()
print(f"Título: {photo['title']}")
print(f"Coordenadas: ({photo['lat']}, {photo['lng']})")

# 4. Obtener metadatos
response = requests.get(f'{BASE_URL}/photos/metadata/filters')
metadata = response.json()
print(f"Épocas disponibles: {metadata['eras']}")
print(f"Rango años: {metadata['yearRange']['min']} - {metadata['yearRange']['max']}")

# 5. Obtener capas
response = requests.get(f'{BASE_URL}/layers')
layers = response.json()
for layer in layers:
    print(f"- {layer['name']} ({layer['type']})")
```

---

## 🔐 Headers recomendados

```bash
# Content-Type (si envías JSON)
curl -H "Content-Type: application/json" http://localhost:3000/api/photos

# Accept (especificar que quieres JSON)
curl -H "Accept: application/json" http://localhost:3000/api/photos

# User-Agent
curl -H "User-Agent: ZaragozaHistorica/1.0" http://localhost:3000/api/photos
```

---

## ⚠️ Manejo de errores

### Error 400 - Bad Request
```json
{
  "error": "bbox debe tener formato: minLng,minLat,maxLng,maxLat"
}
```

### Error 404 - Not Found
```json
{
  "error": "Foto no encontrada"
}
```

### Error 500 - Internal Server Error
```json
{
  "error": "Error interno del servidor"
}
```

---

## 📈 Rate Limiting (futuro)

Por ahora **no hay rate limiting**, pero en producción se recomienda:

```javascript
// Ejemplo con express-rate-limit
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // 100 requests
  message: 'Demasiadas peticiones, intenta de nuevo más tarde'
});

app.use('/api/', limiter);
```

---

## 🎯 Casos de uso reales

### Caso 1: Cargar mapa inicial
```javascript
// 1. Obtener todas las fotos (primera página)
const photos = await fetch('/api/photos?page=1&pageSize=20');

// 2. Obtener metadatos para filtros
const filters = await fetch('/api/photos/metadata/filters');

// 3. Obtener capas del mapa
const layers = await fetch('/api/layers');
```

### Caso 2: Aplicar filtros
```javascript
// Usuario selecciona: Años 50, Casco Histórico, 1940-1960
const response = await fetch('/api/photos?era=Años%2050&zone=Casco%20Histórico&yearFrom=1940&yearTo=1960');
```

### Caso 3: Usuario mueve el mapa
```javascript
// Mapa cambia viewport a nuevos límites
const bounds = map.getBounds();
const bbox = `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`;
const response = await fetch(`/api/photos?bbox=${bbox}`);
```

### Caso 4: Usuario hace clic en una foto
```javascript
// Click en foto con ID 5
const photo = await fetch('/api/photos/5');
// Mostrar modal con detalle completo
```

---

## 📚 Recursos adicionales

- **Postman Collection**: Importa los endpoints desde `backend/postman_collection.json` (crear)
- **Swagger/OpenAPI**: Futuro - documentación interactiva
- **GraphQL**: Alternativa futura a REST

---

¡Listo para empezar a usar la API! 🚀
