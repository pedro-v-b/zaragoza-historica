# Zaragoza Histórica

Archivo visual geolocalizado de la memoria urbana de Zaragoza. Aplicación web cartográfica
que sitúa fotografías históricas de la ciudad en las coordenadas exactas donde fueron
tomadas y las cruza con cartografía histórica oficial del Instituto Geográfico Nacional
(IGN) y con el catastro INSPIRE.

Desarrollado como Trabajo de Fin de Grado del ciclo superior de Desarrollo de Aplicaciones
Multiplataforma (DAM).

- **Producción**: desplegado en Render (frontend estático + backend contenedor Docker)
- **Base de datos**: PostgreSQL 15 con PostGIS 3.4 sobre Supabase
- **Estado**: primera versión pública

---

## Índice

1. [Objetivo del proyecto](#objetivo-del-proyecto)
2. [Características](#características)
3. [Arquitectura](#arquitectura)
4. [Stack tecnológico](#stack-tecnológico)
5. [Modelo de datos](#modelo-de-datos)
6. [API REST](#api-rest)
7. [Instalación local](#instalación-local)
8. [Despliegue](#despliegue)
9. [Estructura del repositorio](#estructura-del-repositorio)
10. [Roadmap](#roadmap)
11. [Créditos y licencia](#créditos-y-licencia)

---

## Objetivo del proyecto

El proyecto consolida un archivo gráfico geolocalizado de Zaragoza: un mapa interactivo
desde el que consultar fotografías históricas asociadas a su punto exacto de captura,
con filtros por periodo cronológico, barrio y época histórica, y con la posibilidad de
superponer cartografía histórica para comparar el trazado actual con representaciones
del territorio de distintos momentos del pasado.

Se dirige al público general, a investigadores, docentes, asociaciones vecinales y
profesionales del patrimonio que necesiten acceder de forma estructurada a material
gráfico histórico con localización precisa.

---

## Características

- Mapa interactivo con clustering de marcadores y carga por viewport
- Fichas de detalle con año, barrio, época, autor, fuente, derechos y descripción
- Visor a pantalla completa con zoom, desplazamiento y gestos táctiles (pinch-zoom)
- Filtros combinables: rango de años, barrio, época histórica y búsqueda textual
- Selector de capas cartográficas con mapas históricos del IGN (WMS) y ortofotos
  del PNOA histórico
- Capa de catastro INSPIRE con coloreado de edificios por década de construcción
- Integración de artículos de Wikipedia y monumentos del patrimonio local
- Panel de administración con autenticación JWT para gestión de fotografías
- Calentamiento automático del backend para mitigar cold starts del plan gratuito
  de Render

---

## Arquitectura

```
                    ┌──────────────────────────┐
                    │  Navegador (cliente web) │
                    └────────────┬─────────────┘
                                 │ HTTPS
                    ┌────────────▼─────────────┐
                    │  Frontend (Render static)│
                    │  React + Vite + Leaflet  │
                    └────────────┬─────────────┘
                                 │ /api/*
                    ┌────────────▼─────────────┐
                    │  Backend (Render docker) │
                    │  FastAPI + psycopg2      │
                    └────────────┬─────────────┘
                                 │ PostgreSQL wire
                    ┌────────────▼─────────────┐
                    │  Supabase (PostGIS 3.4)  │
                    └──────────────────────────┘

   Fuentes externas servidas directamente al mapa:
   IGN WMS (planos/ortofotos) · Wikipedia · Catastro INSPIRE
```

El backend es una API REST sin estado que consulta PostGIS y expone recursos JSON. El
frontend es una SPA estática que consume la API y monta los mapas en Leaflet con
servicios WMS públicos para las capas históricas.

---

## Stack tecnológico

**Backend**

| Componente | Versión | Rol |
|------------|---------|-----|
| Python | 3.11+ | Lenguaje |
| FastAPI | >=0.115 | Framework HTTP y validación |
| Uvicorn | >=0.32 | Servidor ASGI |
| psycopg2-binary | >=2.9 | Driver PostgreSQL |
| Pydantic | >=2.10 | Modelos y settings |
| python-jose | >=3.3 | JWT |
| Pillow | >=10.4 | Procesado de imágenes |
| lxml, pyproj | -- | Importación GML del catastro |

**Frontend**

| Componente | Versión | Rol |
|------------|---------|-----|
| React | 18 | UI |
| TypeScript | 5 | Tipado |
| Vite | 5 | Build y dev server |
| Leaflet | 1.9 | Mapas |
| leaflet.markercluster | 1.5 | Clustering |
| React Router | 6 | Navegación |

**Datos e infraestructura**

- PostgreSQL 15 + PostGIS 3.4 sobre Supabase
- Almacenamiento de imágenes en Supabase Storage (formato WebP)
- Cartografía histórica vía WMS del IGN (PNOA histórico, minutas cartográficas,
  Vuelo Americano 1956-57)
- Catastro INSPIRE vía GML importado a PostGIS
- Despliegue en Render (plan gratuito, frontend estático y backend Docker)

---

## Modelo de datos

### `photos`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | bigserial | Clave primaria |
| `title` | text | Título de la fotografía |
| `description` | text | Descripción libre |
| `year` | int | Año exacto si se conoce |
| `year_from`, `year_to` | int | Rango de años si el año es incierto |
| `era` | text | Época histórica (cadena controlada) |
| `zone` | text | Barrio o distrito |
| `tags` | text[] | Etiquetas libres |
| `lat`, `lng` | double precision | Coordenadas WGS84 |
| `geometry` | geometry(Point, 4326) | Geometría PostGIS indexada |
| `image_url`, `thumb_url` | text | URLs públicas (Supabase Storage) |
| `source`, `author`, `rights` | text | Atribución |

Índices: GIST sobre `geometry`, BTREE sobre `year`, `zone`, `era` y GIN sobre `tags`.

### `buildings`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `inspire_id` | text | Identificador INSPIRE |
| `construction_year` | int | Año de construcción declarado |
| `decade` | int | Década derivada (color del coroplético) |
| `geometry` | geometry(MultiPolygon, 4326) | Huella del edificio |

### `map_layers`

Capas base y superposiciones: URL plantilla de tiles o capa WMS, nombre, año, tipo
(`current`, `plan`, `ortho`) y opcionalmente `bounds` geográficos.

---

## API REST

Base: `/api`. Documentación interactiva en `/docs` (Swagger UI) cuando el backend
corre localmente.

### Fotografías

- `GET /photos` — listado paginado con filtros
- `GET /photos/map` — dataset optimizado para el mapa (campos mínimos)
- `GET /photos/{id}` — ficha completa
- `GET /photos/metadata/filters` — valores disponibles para cada filtro

Parámetros de filtrado admitidos por `GET /photos`:

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `yearFrom`, `yearTo` | int | Rango cronológico |
| `zone` | string | Barrio exacto |
| `era` | string | Época histórica |
| `q` | string | Búsqueda textual en título y descripción |
| `bbox` | string | `minLng,minLat,maxLng,maxLat` para filtrar por viewport |
| `randomOrder` | bool | Orden aleatorio determinista por `seed` |
| `seed` | float | Semilla `[-1, 1]` para el orden aleatorio |
| `page`, `pageSize` | int | Paginación |

### Capas cartográficas

- `GET /layers` — capas base y superposiciones configuradas

### Catastro

- `GET /buildings` — edificios INSPIRE dentro de un `bbox`

### Contextual

- `GET /wikipedia` — artículos georreferenciados dentro de un `bbox`
- `GET /monuments` — monumentos del patrimonio local
- `GET /history` — eventos históricos asociados a un punto o zona

### Administración

- `POST /auth/login` — autenticación JWT
- `POST /photos` — alta
- `PUT /photos/{id}` — edición
- `DELETE /photos/{id}` — baja

### Utilidad

- `GET /health` — health check para orquestadores

---

## Instalación local

### Requisitos

- Python 3.11 o superior
- Node.js 18 o superior
- Docker Desktop si se quiere levantar PostgreSQL con `docker-compose`
- Acceso a un PostgreSQL 15 con la extensión PostGIS habilitada

### Variables de entorno del backend

Crear `backend_python/.env` con:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zaragoza_historica
DB_USER=postgres
DB_PASSWORD=********
JWT_SECRET=********
CORS_ORIGINS=http://localhost:5173
PORT=3000
```

Para producción, las mismas variables apuntan al pooler de Supabase.

### Base de datos

Opción con Docker Compose:

```bash
docker-compose up -d
```

El compose levanta PostgreSQL 15 con PostGIS 3.4 y ejecuta los scripts SQL de
`backend_python/database/` al inicializar el volumen.

Para inicializar un PostgreSQL existente ejecutar manualmente, en orden, los scripts
de `backend_python/database/` y los migradores de `scripts/`.

### Backend

```bash
cd backend_python
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
uvicorn main:app --reload --port 3000
```

La API queda en `http://localhost:3000/api` y la documentación en
`http://localhost:3000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Servidor de desarrollo en `http://localhost:5173`. Vite redirige `/api` al backend
local mediante proxy.

### Datos iniciales

Los datos reales se han cargado en lotes mediante los scripts Python de `scripts/`.
Para un entorno de pruebas basta con la semilla incluida en
`backend_python/database/seeds.sql`. Para replicar la ingesta completa hay que
ejecutar los scripts de scraping (`scraper/`) y los migradores por lotes
(`scripts/batch_*.sql`, `upload_thumbs_webp.py`, `import_buildings.py`).

---

## Despliegue

Render lee `render.yaml` en la raíz del repositorio y define dos servicios:

1. **zaragoza-historica-backend** — servicio web Docker construido desde
   `backend_python/Dockerfile`. Expone el puerto `3000` y consume la contraseña de
   la base de datos como secreto sincronizado en el panel de Render.
2. **zaragoza-historica-frontend** — sitio estático que ejecuta
   `cd frontend && npm install && npm run build` y publica `frontend/dist`. Recibe
   `VITE_API_URL` a partir del host del backend mediante referencia cruzada.

Cualquier push a la rama `master` dispara un rebuild automático de ambos servicios.

El backend corre en el plan gratuito y sufre cold starts. El frontend realiza un
calentamiento contra `/api/health` al cargar la página y muestra un overlay de
progreso hasta que el backend responde.

---

## Estructura del repositorio

```
TFG DAM v2/
├── backend_python/
│   ├── main.py                 Entry point FastAPI
│   ├── config/                 Settings Pydantic
│   ├── database/               Esquema SQL y migraciones
│   ├── dependencies/           Inyección (DB pool, auth)
│   ├── models/                 Modelos Pydantic
│   ├── repositories/           Acceso a datos
│   ├── services/               Lógica de negocio
│   ├── routers/                photos, layers, buildings,
│   │                            wikipedia, monuments, history, auth
│   ├── scripts/                Importadores puntuales (catastro)
│   ├── tests/                  Tests pytest
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/         Layout, Map, Filters, PhotoList,
│       │                        Pages, Admin, Navbar
│       ├── services/api.ts     Cliente HTTP
│       ├── hooks/              Hooks reutilizables
│       ├── utils/              Utilidades (colores catastro, etc.)
│       ├── types/              Tipos compartidos
│       ├── App.tsx             Rutas y contenedor principal
│       └── index.css           Hoja de estilos global
├── scraper/                    Scraping de Flickr y geocoding
├── scripts/                    Migradores SQL por lotes y utilidades
├── docs/                       Documentación complementaria
├── uploads/                    Imágenes locales (entorno de desarrollo)
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## Roadmap

### Publicado

- Mapa interactivo con clustering y carga por viewport
- Filtros por año, barrio, época y búsqueda textual
- Capas cartográficas históricas del IGN (WMS) y ortofotos del PNOA
- Coroplético del catastro INSPIRE por década de construcción
- Fichas detalladas y visor a pantalla completa con pinch-zoom
- Panel de administración con JWT
- Despliegue automático en Render

### Próximas versiones

- Sistema de aportaciones ciudadanas: subida moderada de fotografías por usuarios
  registrados con geolocalización en el mapa
- Ampliación a otros documentos gráficos geolocalizados: cortometrajes, fragmentos
  de películas, videoclips y grabaciones audiovisuales rodadas en la ciudad
- Cruce con hemeroteca: noticias, sucesos y artículos históricos asociados a cada
  punto del mapa
- Búsqueda por texto completo sobre PostgreSQL FTS
- Colecciones y enlaces compartibles con filtros preservados
- Exportación a PDF y KML

---

## Créditos y licencia

- **Autor**: pvial — TFG DAM
- **Año**: 2026
- **Fondo fotográfico**: archivo comunitario *Zaragoza Antigua* (Flickr), utilizado
  con fines educativos y de divulgación del patrimonio
- **Cartografía histórica**: *Instituto Geográfico Nacional* a través de sus
  servicios WMS públicos (PNOA histórico, minutas cartográficas, Vuelo Americano
  1956-57)
- **Catastro**: *Dirección General del Catastro*, datos INSPIRE
- **Infraestructura**: Render (hosting) y Supabase (PostgreSQL + Storage)

Proyecto académico sin fines comerciales. Todos los contenidos externos se usan con
atribución y con finalidad educativa, divulgativa y de puesta en valor del patrimonio.
