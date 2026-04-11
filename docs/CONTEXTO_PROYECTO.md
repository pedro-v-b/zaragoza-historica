# CONTEXTO COMPLETO DEL PROYECTO - Zaragoza Histórica

> Documento generado para compartir el contexto completo del proyecto con una IA.
> Fecha de generación: 19 de febrero de 2026

---

## 1. DESCRIPCIÓN GENERAL

**Nombre**: Zaragoza Histórica
**Tipo**: TFG DAM (Trabajo Fin de Grado - Desarrollo de Aplicaciones Multiplataforma)
**Autor**: pvial
**Estado**: MVP 100% funcional
**Ruta del proyecto**: `c:\Users\pvial\Desktop\TFG DAM`

Aplicación web full-stack para visualizar fotografías históricas geolocalizadas de Zaragoza en un mapa interactivo. Permite explorar fotos antiguas de la ciudad filtradas por año, época, zona y área visible del mapa, con sincronización bidireccional entre el mapa y la lista de resultados.

---

## 2. STACK TECNOLÓGICO

### Backend (Python + FastAPI)
- **Lenguaje**: Python 3.11+
- **Framework**: FastAPI
- **Base de datos**: PostgreSQL 15 + PostGIS 3.4
- **Driver BD**: psycopg2-binary
- **Validación**: Pydantic v2
- **Servidor**: Uvicorn (ASGI)
- **Documentación API**: Swagger UI automático (http://localhost:3000/docs)
- **Puerto**: 3000

### Frontend (React + TypeScript)
- **Framework**: React 18
- **Lenguaje**: TypeScript (strict mode)
- **Build tool**: Vite 5
- **Mapas**: Leaflet 1.9.4 + leaflet.markercluster 1.5.3
- **HTTP Client**: Fetch API nativo
- **Puerto**: 5173

### DevOps
- **Contenedores**: Docker + Docker Compose
- **BD en Docker**: postgis/postgis:15-3.4
- **Backend en Docker**: Python 3.11-slim con Dockerfile propio
- **Variables de entorno**: python-dotenv

---

## 3. ESTRUCTURA DE ARCHIVOS COMPLETA

```
TFG DAM/
├── README.md                          # Documentación principal
├── RESUMEN.md                         # Visión global del proyecto
├── DOCS.md                            # Índice de documentación
├── QUICKSTART.md                      # Guía de inicio rápido
├── MIGRACION_PYTHON.md               # Documentación de migración TS→Python
├── API_EXAMPLES.md                    # Ejemplos de uso de la API
├── INSTALL_POSTGRES.md               # Opciones de instalación de BD
├── GUIA_AÑADIR_FOTOS.md             # Cómo añadir nuevas fotos
├── docker-compose.yml                 # PostgreSQL + Backend Python
├── start.ps1                          # Script de inicio automático (Windows)
├── stop.ps1                           # Script de parada
├── add_photo.py                       # Script interactivo para generar SQL de fotos
│
├── backend/                           # DEPRECADO (antiguo backend TypeScript)
│   ├── database/
│   │   ├── schema.sql
│   │   ├── seeds.sql
│   │   ├── seeds_extra.sql
│   │   └── PLANTILLA_NUEVAS_FOTOS.sql
│   ├── uploads/                       # Imágenes de fotos
│   │   └── thumbs/
│   └── README.md
│
├── backend_python/                    # Backend activo (Python + FastAPI)
│   ├── main.py                        # Entry point FastAPI
│   ├── requirements.txt               # Dependencias Python
│   ├── Dockerfile                     # Contenedor Python
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py               # Pool de conexiones PostgreSQL
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                # Modelos Pydantic
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── photos.py                 # Endpoints de fotos
│   │   └── layers.py                 # Endpoints de capas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── photos_service.py         # Lógica de negocio fotos
│   │   └── layers_service.py         # Lógica de negocio capas
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── photos_repository.py      # Queries PostGIS + filtros
│   │   └── layers_repository.py      # Queries capas
│   └── database/
│       ├── schema.sql                # Tablas + PostGIS + índices + triggers
│       ├── seeds.sql                 # 8 fotos + 3 capas de ejemplo
│       ├── seeds_extra.sql           # 10 fotos adicionales opcionales
│       └── PLANTILLA_NUEVAS_FOTOS.sql
│
├── frontend/                          # Frontend React
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts                # Config Vite + proxy /api → localhost:3000
│   └── src/
│       ├── main.tsx                   # Entry point React
│       ├── App.tsx                    # Orquestación principal
│       ├── index.css                  # Estilos globales (~429 líneas)
│       ├── vite-env.d.ts
│       ├── components/
│       │   ├── Layout/
│       │   │   ├── Layout.tsx         # Layout 3 paneles
│       │   │   ├── Header.tsx         # Cabecera con título
│       │   │   └── index.ts
│       │   ├── Map/
│       │   │   ├── MapView.tsx        # Mapa Leaflet + marcadores + capas
│       │   │   └── index.ts
│       │   ├── Filters/
│       │   │   ├── Filters.tsx        # Panel de filtros dinámicos
│       │   │   └── index.ts
│       │   └── PhotoList/
│       │       ├── PhotoList.tsx      # Lista + paginación
│       │       └── index.ts
│       ├── hooks/
│       │   └── useDebounce.ts         # Hook de debounce
│       ├── services/
│       │   └── api.ts                 # Cliente HTTP para backend
│       └── types/
│           └── index.ts               # Interfaces TypeScript
│
└── uploads/                           # Directorio de uploads compartido
```

---

## 4. ARQUITECTURA DEL BACKEND

### Patrón: 4 capas (Routers → Services → Repositories → Database)

```
Petición HTTP
    ↓
[Routers]        → Define endpoints, validación de parámetros (FastAPI + Query)
    ↓
[Services]       → Lógica de negocio, transformación de datos (Pydantic)
    ↓
[Repositories]   → Queries SQL directas con psycopg2 (PostGIS)
    ↓
[Database]       → Pool de conexiones PostgreSQL (SimpleConnectionPool)
```

### Archivo: `backend_python/main.py`
```python
"""
Zaragoza Histórica - Backend API con FastAPI
Aplicación para visualizar fotografías históricas geolocalizadas de Zaragoza
"""
import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from config.database import Database
from routers import photos, layers

# Cargar variables de entorno
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    print("\n🚀 Iniciando Zaragoza Histórica API...")
    
    # Verificar conexión a base de datos
    db_connected = await Database.test_connection()
    
    if not db_connected:
        print("❌ No se pudo conectar a la base de datos. Abortando inicio del servidor.")
        exit(1)
    
    print("✅ API lista para recibir peticiones\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Cerrando Zaragoza Histórica API...")
    Database.close_all()
    print("✅ Conexiones cerradas correctamente\n")


# Crear aplicación FastAPI
app = FastAPI(
    title="Zaragoza Histórica API",
    description="API REST para visualizar fotografías históricas geolocalizadas de Zaragoza",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (uploads)
uploads_path = os.path.join(os.path.dirname(__file__), "..", "uploads")
if os.path.exists(os.path.abspath(uploads_path)):
    app.mount("/uploads", StaticFiles(directory=os.path.abspath(uploads_path)), name="uploads")
else:
    os.makedirs(os.path.abspath(uploads_path), exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=os.path.abspath(uploads_path)), name="uploads")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return JSONResponse({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    })


# Incluir routers
app.include_router(photos.router, prefix="/api")
app.include_router(layers.router, prefix="/api")


# Manejador de 404
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint no encontrado"}
    )


# Punto de entrada
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"\n🚀 Servidor Zaragoza Histórica iniciado")
    print(f"📍 URL: http://localhost:{port}")
    print(f"🗺️  API: http://localhost:{port}/api")
    print(f"📚 Docs: http://localhost:{port}/docs")
    print(f"🏥 Health: http://localhost:{port}/api/health\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
```

### Archivo: `backend_python/config/database.py`
```python
"""
Configuración de conexión a PostgreSQL + PostGIS
"""
import os
import sys
from typing import Optional
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configurar codificación en Windows antes de todo
if sys.platform == 'win32':
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except:
            pass

load_dotenv()

class Database:
    """Gestor de conexiones a PostgreSQL"""
    
    _connection_pool: Optional[pool.SimpleConnectionPool] = None
    _initialized = False
    _conn_params = None
    
    @classmethod
    def _get_conn_params(cls):
        if cls._conn_params is None:
            cls._conn_params = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'database': os.getenv('DB_NAME', 'zaragoza_historica'),
                'user': os.getenv('DB_USER', 'zaragoza_user'),
                'password': os.getenv('DB_PASSWORD', 'zaragoza_pass'),
            }
        return cls._conn_params
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        if cls._connection_pool is None:
            try:
                params = cls._get_conn_params()
                conn_string = (
                    f"host={params['host']} "
                    f"port={params['port']} "
                    f"dbname={params['database']} "
                    f"user={params['user']} "
                    f"password={params['password']} "
                    f"client_encoding=UTF8"
                )
                cls._connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dsn=conn_string,
                    cursor_factory=RealDictCursor
                )
                cls._initialized = True
            except Exception as e:
                print(f"❌ Error creando pool de conexiones: {e}")
                raise
    
    @classmethod
    def get_connection(cls):
        if not cls._initialized:
            cls.initialize()
        return cls._connection_pool.getconn()
    
    @classmethod
    def return_connection(cls, conn):
        if cls._connection_pool is not None:
            cls._connection_pool.putconn(conn)
    
    @classmethod
    def close_all(cls):
        if cls._connection_pool is not None:
            cls._connection_pool.closeall()
```

### Archivo: `backend_python/models/schemas.py`
```python
"""
Modelos Pydantic para validación y serialización
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class Photo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    year: Optional[int] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    era: Optional[str] = None
    zone: Optional[str] = None
    lat: float
    lng: float
    image_url: str
    thumb_url: str
    source: Optional[str] = None
    author: Optional[str] = None
    rights: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PhotoFilters(BaseModel):
    bbox: Optional[str] = Field(None, description="Bounding box: 'minLng,minLat,maxLng,maxLat'")
    yearFrom: Optional[int] = Field(None, alias="yearFrom")
    yearTo: Optional[int] = Field(None, alias="yearTo")
    era: Optional[str] = None
    zone: Optional[str] = None
    q: Optional[str] = Field(None, description="Búsqueda de texto")
    page: int = Field(1, ge=1)
    pageSize: int = Field(20, ge=1, le=100, alias="pageSize")

    class Config:
        populate_by_name = True


class PaginatedPhotos(BaseModel):
    items: List[Photo]
    total: int
    page: int
    pageSize: int = Field(alias="pageSize")
    totalPages: int = Field(alias="totalPages")

    class Config:
        populate_by_name = True


class Bounds(BaseModel):
    north: float
    south: float
    east: float
    west: float


class MapLayer(BaseModel):
    id: int
    name: str
    year: Optional[int] = None
    type: Literal['plan', 'ortho', 'current']
    tile_url_template: Optional[str] = None
    attribution: Optional[str] = None
    min_zoom: int = Field(alias="min_zoom")
    max_zoom: int = Field(alias="max_zoom")
    bounds: Optional[Bounds] = None
    is_active: bool = Field(alias="is_active")
    display_order: int = Field(alias="display_order")

    class Config:
        populate_by_name = True
        from_attributes = True


class FilterMetadata(BaseModel):
    eras: List[str]
    zones: List[str]
    yearRange: dict = Field(alias="yearRange")

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
```

### Archivo: `backend_python/routers/photos.py`
```python
"""
Router para endpoints de fotos
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import PaginatedPhotos, FilterMetadata, Photo
from services.photos_service import photos_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/metadata/filters", response_model=FilterMetadata)
async def get_filter_metadata():
    return photos_service.get_filter_metadata()


@router.get("/{photo_id}", response_model=Photo)
async def get_photo_by_id(photo_id: int):
    photo = photos_service.get_photo_by_id(photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail=f"Foto con ID {photo_id} no encontrada")
    return photo


@router.get("", response_model=PaginatedPhotos)
async def get_photos(
    bbox: Optional[str] = Query(None, description="Bounding box: 'minLng,minLat,maxLng,maxLat'"),
    yearFrom: Optional[int] = Query(None, description="Año desde"),
    yearTo: Optional[int] = Query(None, description="Año hasta"),
    era: Optional[str] = Query(None, description="Época histórica"),
    zone: Optional[str] = Query(None, description="Zona de Zaragoza"),
    q: Optional[str] = Query(None, description="Búsqueda de texto"),
    page: int = Query(1, ge=1, description="Número de página"),
    pageSize: int = Query(20, ge=1, le=100, description="Resultados por página")
):
    filters = {
        'bbox': bbox, 'yearFrom': yearFrom, 'yearTo': yearTo,
        'era': era, 'zone': zone, 'q': q, 'page': page, 'pageSize': pageSize
    }
    return photos_service.get_photos(filters)
```

### Archivo: `backend_python/routers/layers.py`
```python
"""
Router para endpoints de capas del mapa
"""
from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import MapLayer
from services.layers_service import layers_service

router = APIRouter(prefix="/layers", tags=["layers"])


@router.get("/{layer_id}", response_model=MapLayer)
async def get_layer_by_id(layer_id: int):
    layer = layers_service.get_layer_by_id(layer_id)
    if not layer:
        raise HTTPException(status_code=404, detail=f"Capa con ID {layer_id} no encontrada")
    return layer


@router.get("", response_model=List[MapLayer])
async def get_layers():
    return layers_service.get_layers()
```

### Archivo: `backend_python/services/photos_service.py`
```python
"""
Servicio de lógica de negocio para fotos
"""
from typing import Dict
from models.schemas import PaginatedPhotos, FilterMetadata, Photo
from repositories.photos_repository import photos_repository
import math


class PhotosService:
    def get_photos(self, filters: dict) -> PaginatedPhotos:
        photos_data, total = photos_repository.find_all(filters)
        page = filters.get('page', 1)
        page_size = filters.get('pageSize', 20)
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        photos = [Photo(**photo) for photo in photos_data]
        return PaginatedPhotos(
            items=photos, total=total, page=page,
            pageSize=page_size, totalPages=total_pages
        )
    
    def get_photo_by_id(self, photo_id: int) -> Photo:
        photo_data = photos_repository.find_by_id(photo_id)
        if not photo_data:
            return None
        return Photo(**photo_data)
    
    def get_filter_metadata(self) -> FilterMetadata:
        eras = photos_repository.get_distinct_eras()
        zones = photos_repository.get_distinct_zones()
        year_range = photos_repository.get_year_range()
        return FilterMetadata(eras=eras, zones=zones, yearRange=year_range)


photos_service = PhotosService()
```

### Archivo: `backend_python/services/layers_service.py`
```python
"""
Servicio de lógica de negocio para capas
"""
from typing import List
from models.schemas import MapLayer
from repositories.layers_repository import layers_repository


class LayersService:
    def get_layers(self) -> List[MapLayer]:
        layers_data = layers_repository.find_all()
        return [MapLayer(**layer) for layer in layers_data]
    
    def get_layer_by_id(self, layer_id: int) -> MapLayer:
        layer_data = layers_repository.find_by_id(layer_id)
        if not layer_data:
            return None
        return MapLayer(**layer_data)


layers_service = LayersService()
```

### Archivo: `backend_python/repositories/photos_repository.py`
```python
"""
Repository para operaciones sobre fotos históricas con PostGIS
"""
from typing import List, Tuple, Dict, Optional
from config.database import Database


class PhotosRepository:
    def find_all(self, filters: dict) -> Tuple[List[dict], int]:
        bbox = filters.get('bbox')
        year_from = filters.get('yearFrom')
        year_to = filters.get('yearTo')
        era = filters.get('era')
        zone = filters.get('zone')
        q = filters.get('q')
        page = filters.get('page', 1)
        page_size = filters.get('pageSize', 20)
        
        where_clauses = []
        query_params = []
        
        # Filtro por bounding box (PostGIS)
        if bbox:
            coords = bbox.split(',')
            min_lng, min_lat, max_lng, max_lat = map(float, coords)
            where_clauses.append(
                "ST_Intersects(geometry, ST_MakeEnvelope(%s, %s, %s, %s, 4326))"
            )
            query_params.extend([min_lng, min_lat, max_lng, max_lat])
        
        # Filtro por rango de años
        if year_from is not None:
            where_clauses.append("(year >= %s OR year_to >= %s)")
            query_params.extend([year_from, year_from])
        if year_to is not None:
            where_clauses.append("(year <= %s OR year_from <= %s)")
            query_params.extend([year_to, year_to])
        
        # Filtro por época
        if era:
            where_clauses.append("era = %s")
            query_params.append(era)
        
        # Filtro por zona
        if zone:
            where_clauses.append("zone = %s")
            query_params.append(zone)
        
        # Búsqueda de texto (ILIKE en título, descripción y tags)
        if q:
            where_clauses.append(
                "(title ILIKE %s OR description ILIKE %s OR array_to_string(tags, ' ') ILIKE %s)"
            )
            search_term = f"%{q}%"
            query_params.extend([search_term, search_term, search_term])
        
        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            
            # Count total
            cursor.execute(f"SELECT COUNT(*) as count FROM photos {where_clause}", query_params)
            total = cursor.fetchone()['count']
            
            # Fotos paginadas
            offset = (page - 1) * page_size
            cursor.execute(f"""
                SELECT id, title, description, year, year_from, year_to, era, zone,
                    lat, lng, image_url, thumb_url, source, author, rights, tags,
                    created_at, updated_at
                FROM photos {where_clause}
                ORDER BY year DESC NULLS LAST, created_at DESC
                LIMIT %s OFFSET %s
            """, query_params + [page_size, offset])
            photos = cursor.fetchall()
            cursor.close()
            return [dict(photo) for photo in photos], total
        finally:
            Database.return_connection(conn)
    
    def find_by_id(self, photo_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, year, year_from, year_to, era, zone,
                    lat, lng, image_url, thumb_url, source, author, rights, tags,
                    created_at, updated_at
                FROM photos WHERE id = %s
            """, (photo_id,))
            photo = cursor.fetchone()
            cursor.close()
            return dict(photo) if photo else None
        finally:
            Database.return_connection(conn)
    
    def get_distinct_eras(self) -> List[str]:
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT era FROM photos WHERE era IS NOT NULL ORDER BY era")
            results = cursor.fetchall()
            cursor.close()
            return [row['era'] for row in results]
        finally:
            Database.return_connection(conn)
    
    def get_distinct_zones(self) -> List[str]:
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT zone FROM photos WHERE zone IS NOT NULL ORDER BY zone")
            results = cursor.fetchall()
            cursor.close()
            return [row['zone'] for row in results]
        finally:
            Database.return_connection(conn)
    
    def get_year_range(self) -> Dict[str, int]:
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MIN(COALESCE(year, year_from)) as min_year,
                       MAX(COALESCE(year, year_to)) as max_year
                FROM photos
            """)
            result = cursor.fetchone()
            cursor.close()
            return {'min': result['min_year'] or 1800, 'max': result['max_year'] or 2024}
        finally:
            Database.return_connection(conn)


photos_repository = PhotosRepository()
```

### Archivo: `backend_python/repositories/layers_repository.py`
```python
"""
Repository para capas del mapa
"""
from typing import List, Optional
from config.database import Database


class LayersRepository:
    def find_all(self) -> List[dict]:
        query = """
            SELECT id, name, year, type, tile_url_template, attribution,
                min_zoom, max_zoom, bounds_north, bounds_south, bounds_east, bounds_west,
                is_active, display_order
            FROM map_layers WHERE is_active = true ORDER BY display_order ASC
        """
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            layers = []
            for row in results:
                layer = dict(row)
                if layer.get('bounds_north') is not None:
                    layer['bounds'] = {
                        'north': layer['bounds_north'], 'south': layer['bounds_south'],
                        'east': layer['bounds_east'], 'west': layer['bounds_west']
                    }
                else:
                    layer['bounds'] = None
                for key in ['bounds_north', 'bounds_south', 'bounds_east', 'bounds_west']:
                    layer.pop(key, None)
                layers.append(layer)
            return layers
        finally:
            Database.return_connection(conn)
    
    def find_by_id(self, layer_id: int) -> Optional[dict]:
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, year, type, tile_url_template, attribution,
                    min_zoom, max_zoom, bounds_north, bounds_south, bounds_east, bounds_west,
                    is_active, display_order
                FROM map_layers WHERE id = %s
            """, (layer_id,))
            row = cursor.fetchone()
            cursor.close()
            if not row:
                return None
            layer = dict(row)
            if layer.get('bounds_north') is not None:
                layer['bounds'] = {
                    'north': layer['bounds_north'], 'south': layer['bounds_south'],
                    'east': layer['bounds_east'], 'west': layer['bounds_west']
                }
            else:
                layer['bounds'] = None
            for key in ['bounds_north', 'bounds_south', 'bounds_east', 'bounds_west']:
                layer.pop(key, None)
            return layer
        finally:
            Database.return_connection(conn)


layers_repository = LayersRepository()
```

### Archivo: `backend_python/requirements.txt`
```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.9
pydantic>=2.10.0
pydantic-settings>=2.7.0
python-multipart>=0.0.6
```

### Archivo: `backend_python/Dockerfile`
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/uploads/thumbs
EXPOSE 3000
ENV PYTHONUNBUFFERED=1
ENV PORT=3000
```

---

## 5. FRONTEND COMPLETO

### Archivo: `frontend/src/App.tsx`
```tsx
import { useState, useEffect, useCallback } from 'react';
import { Layout, Header } from './components/Layout';
import { Filters } from './components/Filters';
import { MapView } from './components/Map';
import { PhotoList } from './components/PhotoList';
import { Photo } from './types';
import { getPhotos } from './services/api';
import { useDebounce } from './hooks/useDebounce';
import './index.css';

function App() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(false);

  const [yearFrom, setYearFrom] = useState<number | undefined>();
  const [yearTo, setYearTo] = useState<number | undefined>();
  const [era, setEra] = useState<string | undefined>();
  const [zone, setZone] = useState<string | undefined>();
  const [searchQuery, setSearchQuery] = useState<string | undefined>();
  const [bbox, setBbox] = useState<string | undefined>();
  const [onlyInViewport, setOnlyInViewport] = useState(false);

  const [selectedPhotoId, setSelectedPhotoId] = useState<number | null>(null);
  const [centerOnPhoto, setCenterOnPhoto] = useState<Photo | null>(null);

  const debouncedBbox = useDebounce(bbox, 800);

  useEffect(() => {
    loadPhotos();
  }, [yearFrom, yearTo, era, zone, searchQuery, page, debouncedBbox, onlyInViewport]);

  const loadPhotos = async () => {
    setLoading(true);
    try {
      const filters: any = { page, pageSize };
      if (yearFrom) filters.yearFrom = yearFrom;
      if (yearTo) filters.yearTo = yearTo;
      if (era) filters.era = era;
      if (zone) filters.zone = zone;
      if (searchQuery) filters.q = searchQuery;
      if (onlyInViewport && debouncedBbox) filters.bbox = debouncedBbox;

      const response = await getPhotos(filters);
      setPhotos(response.items);
      setTotal(response.total);
      setTotalPages(response.totalPages);
    } catch (error) {
      console.error('Error loading photos:', error);
      setPhotos([]);
      setTotal(0);
      setTotalPages(0);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = useCallback(
    (filters: { yearFrom?: number; yearTo?: number; era?: string; zone?: string; q?: string; onlyInViewport: boolean; }) => {
      setYearFrom(filters.yearFrom);
      setYearTo(filters.yearTo);
      setEra(filters.era);
      setZone(filters.zone);
      setSearchQuery(filters.q);
      setOnlyInViewport(filters.onlyInViewport);
      setPage(1);
    }, []
  );

  const handleMapMove = useCallback((newBbox: string) => { setBbox(newBbox); }, []);
  const handlePhotoClick = useCallback((photo: Photo) => {
    setSelectedPhotoId(photo.id);
    setCenterOnPhoto(photo);
  }, []);
  const handlePageChange = useCallback((newPage: number) => { setPage(newPage); }, []);

  return (
    <Layout>
      <div className="sidebar-left">
        <Header />
        <Filters onFilterChange={handleFilterChange} />
      </div>
      <MapView photos={photos} selectedPhotoId={selectedPhotoId}
        onMapMove={handleMapMove} onPhotoClick={handlePhotoClick} centerOnPhoto={centerOnPhoto} />
      <div className="sidebar-right">
        <PhotoList photos={photos} total={total} page={page} pageSize={pageSize}
          totalPages={totalPages} loading={loading} selectedPhotoId={selectedPhotoId}
          onPhotoClick={handlePhotoClick} onPageChange={handlePageChange} />
      </div>
    </Layout>
  );
}

export default App;
```

### Archivo: `frontend/src/types/index.ts`
```typescript
export interface Photo {
  id: number;
  title: string;
  description?: string;
  year?: number;
  year_from?: number;
  year_to?: number;
  era?: string;
  zone?: string;
  lat: number;
  lng: number;
  image_url: string;
  thumb_url: string;
  source?: string;
  author?: string;
  rights?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface PhotoFilters {
  bbox?: string;
  yearFrom?: number;
  yearTo?: number;
  era?: string;
  zone?: string;
  q?: string;
  page?: number;
  pageSize?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface MapLayer {
  id: number;
  name: string;
  year?: number;
  type: 'plan' | 'ortho' | 'current';
  tile_url_template?: string;
  attribution?: string;
  min_zoom: number;
  max_zoom: number;
  bounds?: { north: number; south: number; east: number; west: number; };
  is_active: boolean;
  display_order: number;
}

export interface FilterMetadata {
  eras: string[];
  zones: string[];
  yearRange: { min: number; max: number; };
}

export interface BBox {
  minLng: number;
  minLat: number;
  maxLng: number;
  maxLat: number;
}
```

### Archivo: `frontend/src/services/api.ts`
```typescript
import { Photo, PhotoFilters, PaginatedResponse, MapLayer, FilterMetadata } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export async function getPhotos(filters: PhotoFilters): Promise<PaginatedResponse<Photo>> {
  const params = new URLSearchParams();
  if (filters.bbox) params.append('bbox', filters.bbox);
  if (filters.yearFrom !== undefined) params.append('yearFrom', filters.yearFrom.toString());
  if (filters.yearTo !== undefined) params.append('yearTo', filters.yearTo.toString());
  if (filters.era) params.append('era', filters.era);
  if (filters.zone) params.append('zone', filters.zone);
  if (filters.q) params.append('q', filters.q);
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.pageSize) params.append('pageSize', filters.pageSize.toString());

  const response = await fetch(`${API_BASE_URL}/photos?${params.toString()}`);
  if (!response.ok) throw new Error(`Error fetching photos: ${response.statusText}`);
  return response.json();
}

export async function getPhotoById(id: number): Promise<Photo> {
  const response = await fetch(`${API_BASE_URL}/photos/${id}`);
  if (!response.ok) throw new Error(`Error fetching photo ${id}: ${response.statusText}`);
  return response.json();
}

export async function getFilterMetadata(): Promise<FilterMetadata> {
  const response = await fetch(`${API_BASE_URL}/photos/metadata/filters`);
  if (!response.ok) throw new Error(`Error fetching filter metadata: ${response.statusText}`);
  return response.json();
}

export async function getMapLayers(): Promise<MapLayer[]> {
  const response = await fetch(`${API_BASE_URL}/layers`);
  if (!response.ok) throw new Error(`Error fetching map layers: ${response.statusText}`);
  return response.json();
}
```

### Archivo: `frontend/src/components/Map/MapView.tsx`
```tsx
import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet.markercluster';
import { Photo, MapLayer } from '../../types';
import { getMapLayers } from '../../services/api';

// Fix para iconos de Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

interface MapViewProps {
  photos: Photo[];
  selectedPhotoId: number | null;
  onMapMove: (bbox: string) => void;
  onPhotoClick: (photo: Photo) => void;
  centerOnPhoto?: Photo | null;
}

export const MapView: React.FC<MapViewProps> = ({
  photos, selectedPhotoId, onMapMove, onPhotoClick, centerOnPhoto,
}) => {
  const mapRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [layers, setLayers] = useState<MapLayer[]>([]);
  const [currentLayerId, setCurrentLayerId] = useState<number | null>(null);
  const baseLayersRef = useRef<{ [key: number]: L.TileLayer }>({});
  const initializedRef = useRef<boolean>(false);

  // Inicializar mapa centrado en Zaragoza (Plaza del Pilar)
  useEffect(() => {
    if (!containerRef.current || initializedRef.current) return;
    initializedRef.current = true;

    const map = L.map(containerRef.current, {
      center: [41.6488, -0.8891],
      zoom: 13, zoomControl: true, minZoom: 3, maxZoom: 19, preferCanvas: true,
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap', maxZoom: 19, minZoom: 3,
    }).addTo(map);

    mapRef.current = map;
    const markersLayer = L.layerGroup();
    markersLayer.addTo(map);
    markersLayerRef.current = markersLayer;

    loadMapLayers();

    let moveTimeout: ReturnType<typeof setTimeout>;
    map.on('moveend', () => {
      clearTimeout(moveTimeout);
      moveTimeout = setTimeout(() => {
        const bounds = map.getBounds();
        onMapMove(`${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`);
      }, 500);
    });

    return () => { initializedRef.current = false; map.remove(); };
  }, []);

  const loadMapLayers = async () => {
    try {
      const layersData = await getMapLayers();
      setLayers(layersData);
      if (layersData.length > 0) setCurrentLayerId(layersData[0].id);
    } catch (error) { console.error('Error loading map layers:', error); }
  };

  // Actualizar marcadores
  useEffect(() => {
    if (!mapRef.current || !markersLayerRef.current) return;
    markersLayerRef.current.clearLayers();
    photos.forEach((photo) => {
      const marker = L.marker([photo.lat, photo.lng]);
      const popupContent = `
        <div class="popup-content">
          <img src="${photo.thumb_url}" alt="${photo.title}" onerror="this.src='https://via.placeholder.com/200?text=Sin+imagen'" />
          <h3>${photo.title}</h3>
          <p><strong>Año:</strong> ${photo.year || `${photo.year_from || '?'} - ${photo.year_to || '?'}`}</p>
          ${photo.zone ? `<p><strong>Zona:</strong> ${photo.zone}</p>` : ''}
          <button class="btn btn-primary" onclick="window.handlePhotoClick(${photo.id})">Ver detalle completo</button>
        </div>`;
      marker.bindPopup(popupContent, { maxWidth: 250 });
      if (photo.id === selectedPhotoId) {
        marker.setIcon(L.icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
          shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
          iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
        }));
      }
      markersLayerRef.current!.addLayer(marker);
    });
  }, [photos, selectedPhotoId]);

  // Centrar en foto seleccionada
  useEffect(() => {
    if (centerOnPhoto && mapRef.current) {
      mapRef.current.setView([centerOnPhoto.lat, centerOnPhoto.lng], 16, { animate: true });
    }
  }, [centerOnPhoto]);

  // Exponer función para popups
  useEffect(() => {
    (window as any).handlePhotoClick = (photoId: number) => {
      const photo = photos.find((p) => p.id === photoId);
      if (photo) onPhotoClick(photo);
    };
    return () => { delete (window as any).handlePhotoClick; };
  }, [photos, onPhotoClick]);

  // Cambiar capa base
  const handleLayerChange = (layerId: number) => {
    if (!mapRef.current) return;
    const map = mapRef.current;
    const layer = layers.find((l) => l.id === layerId);
    if (!layer) return;
    Object.values(baseLayersRef.current).forEach((l) => map.removeLayer(l));
    if (layer.tile_url_template) {
      if (!baseLayersRef.current[layerId]) {
        baseLayersRef.current[layerId] = L.tileLayer(layer.tile_url_template, {
          attribution: layer.attribution || '', minZoom: layer.min_zoom, maxZoom: layer.max_zoom,
        });
      }
      baseLayersRef.current[layerId].addTo(map);
    } else {
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: layer.attribution || '&copy; OpenStreetMap',
      }).addTo(map);
    }
    setCurrentLayerId(layerId);
  };

  return (
    <div className="map-container">
      <div ref={containerRef} style={{ height: '100%', width: '100%' }} />
      {layers.length > 0 && (
        <div className="layer-control">
          <h4>🗺️ Capas del mapa</h4>
          {layers.map((layer) => (
            <label key={layer.id}>
              <input type="radio" name="layer" checked={currentLayerId === layer.id}
                onChange={() => handleLayerChange(layer.id)} />
              {layer.name}{layer.year && ` (${layer.year})`}{!layer.tile_url_template && ' 📌'}
            </label>
          ))}
          <p style={{ fontSize: '11px', color: '#999', marginTop: '10px' }}>📌 = Capa en desarrollo</p>
        </div>
      )}
    </div>
  );
};
```

### Archivo: `frontend/src/components/Filters/Filters.tsx`
```tsx
import React, { useState, useEffect } from 'react';
import { FilterMetadata } from '../../types';
import { getFilterMetadata } from '../../services/api';

interface FiltersProps {
  onFilterChange: (filters: {
    yearFrom?: number; yearTo?: number; era?: string;
    zone?: string; q?: string; onlyInViewport: boolean;
  }) => void;
}

export const Filters: React.FC<FiltersProps> = ({ onFilterChange }) => {
  const [metadata, setMetadata] = useState<FilterMetadata | null>(null);
  const [yearFrom, setYearFrom] = useState<string>('');
  const [yearTo, setYearTo] = useState<string>('');
  const [era, setEra] = useState<string>('');
  const [zone, setZone] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [onlyInViewport, setOnlyInViewport] = useState<boolean>(false);

  useEffect(() => { loadMetadata(); }, []);

  const loadMetadata = async () => {
    try { setMetadata(await getFilterMetadata()); }
    catch (error) { console.error('Error loading filter metadata:', error); }
  };

  const handleApplyFilters = () => {
    onFilterChange({
      yearFrom: yearFrom ? parseInt(yearFrom, 10) : undefined,
      yearTo: yearTo ? parseInt(yearTo, 10) : undefined,
      era: era || undefined, zone: zone || undefined,
      q: searchQuery || undefined, onlyInViewport,
    });
  };

  const handleResetFilters = () => {
    setYearFrom(''); setYearTo(''); setEra(''); setZone('');
    setSearchQuery(''); setOnlyInViewport(false);
    onFilterChange({ onlyInViewport: false });
  };

  return (
    <div className="filters-panel">
      <div className="filter-section">
        <h3>Búsqueda</h3>
        <input type="text" placeholder="Buscar en título, descripción o tags..."
          value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleApplyFilters()} />
      </div>
      <div className="filter-section">
        <h3>Rango de años</h3>
        {metadata && <p style={{ fontSize: '12px', color: '#999', marginBottom: '10px' }}>
          Disponible: {metadata.yearRange.min} - {metadata.yearRange.max}</p>}
        <div className="year-inputs">
          <div><label>Desde</label>
            <input type="number" placeholder={metadata?.yearRange.min.toString()} value={yearFrom}
              onChange={(e) => setYearFrom(e.target.value)} /></div>
          <div><label>Hasta</label>
            <input type="number" placeholder={metadata?.yearRange.max.toString()} value={yearTo}
              onChange={(e) => setYearTo(e.target.value)} /></div>
        </div>
      </div>
      <div className="filter-section">
        <h3>Época</h3>
        <select value={era} onChange={(e) => setEra(e.target.value)}>
          <option value="">Todas las épocas</option>
          {metadata?.eras.map((e) => <option key={e} value={e}>{e}</option>)}
        </select>
      </div>
      <div className="filter-section">
        <h3>Zona</h3>
        <select value={zone} onChange={(e) => setZone(e.target.value)}>
          <option value="">Todas las zonas</option>
          {metadata?.zones.map((z) => <option key={z} value={z}>{z}</option>)}
        </select>
      </div>
      <div className="filter-section">
        <div className="checkbox-filter">
          <input type="checkbox" id="onlyInViewport" checked={onlyInViewport}
            onChange={(e) => setOnlyInViewport(e.target.checked)} />
          <label htmlFor="onlyInViewport">Solo fotos en pantalla del mapa</label>
        </div>
      </div>
      <div className="filter-section">
        <div className="filter-actions">
          <button className="btn btn-primary" onClick={handleApplyFilters}>Aplicar filtros</button>
          <button className="btn btn-secondary" onClick={handleResetFilters}>Limpiar</button>
        </div>
      </div>
    </div>
  );
};
```

### Archivo: `frontend/src/components/PhotoList/PhotoList.tsx`
```tsx
import React from 'react';
import { Photo } from '../../types';

interface PhotoListProps {
  photos: Photo[]; total: number; page: number; pageSize: number;
  totalPages: number; loading: boolean; selectedPhotoId: number | null;
  onPhotoClick: (photo: Photo) => void; onPageChange: (page: number) => void;
}

export const PhotoList: React.FC<PhotoListProps> = ({
  photos, total, page, pageSize, totalPages, loading, selectedPhotoId, onPhotoClick, onPageChange,
}) => {
  const formatYear = (photo: Photo): string => {
    if (photo.year) return photo.year.toString();
    if (photo.year_from && photo.year_to) return `${photo.year_from}-${photo.year_to}`;
    if (photo.year_from) return `Desde ${photo.year_from}`;
    if (photo.year_to) return `Hasta ${photo.year_to}`;
    return 'Fecha desconocida';
  };

  if (loading) return <div className="photo-list"><div className="loading"><p>Cargando fotos...</p></div></div>;
  if (photos.length === 0) return <div className="photo-list"><div className="empty-state"><p>No se encontraron fotos</p></div></div>;

  return (
    <div className="photo-list">
      <div className="photo-list-header">
        <h2>Resultados</h2>
        <div className="results-info">Mostrando {photos.length} de {total} fotos</div>
      </div>
      <div className="photo-items">
        {photos.map((photo) => (
          <div key={photo.id} className={`photo-card ${selectedPhotoId === photo.id ? 'active' : ''}`}
            onClick={() => onPhotoClick(photo)}>
            <div className="photo-card-thumbnail">
              <img src={photo.thumb_url} alt={photo.title}
                onError={(e) => { (e.target as HTMLImageElement).src = 'https://via.placeholder.com/100?text=Sin+imagen'; }} />
            </div>
            <div className="photo-card-content">
              <div className="photo-card-title">{photo.title}</div>
              <div className="photo-card-year">{formatYear(photo)}</div>
              {photo.zone && <div className="photo-card-zone">{photo.zone}</div>}
              {photo.description && <div className="photo-card-description">{photo.description}</div>}
            </div>
          </div>
        ))}
      </div>
      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => onPageChange(page - 1)} disabled={page === 1}>← Anterior</button>
          <span className="pagination-info">Página {page} de {totalPages}</span>
          <button onClick={() => onPageChange(page + 1)} disabled={page === totalPages}>Siguiente →</button>
        </div>
      )}
    </div>
  );
};
```

### Archivo: `frontend/src/components/Layout/Layout.tsx`
```tsx
import React from 'react';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <div className="app-layout">{children}</div>;
};
```

### Archivo: `frontend/src/components/Layout/Header.tsx`
```tsx
import React from 'react';

export const Header: React.FC = () => {
  return (
    <div className="app-header">
      <h1>Zaragoza Histórica</h1>
      <p>Explora fotografías históricas geolocalizadas de Zaragoza</p>
    </div>
  );
};
```

### Archivo: `frontend/src/hooks/useDebounce.ts`
```typescript
import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const handler = setTimeout(() => { setDebouncedValue(value); }, delay);
    return () => { clearTimeout(handler); };
  }, [value, delay]);
  return debouncedValue;
}
```

### Archivo: `frontend/vite.config.ts`
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
})
```

### Archivo: `frontend/package.json`
```json
{
  "name": "zaragoza-historica-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "leaflet": "^1.9.4",
    "leaflet.markercluster": "^1.5.3"
  },
  "devDependencies": {
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "@types/leaflet": "^1.9.8",
    "@types/leaflet.markercluster": "^1.5.4",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.8"
  }
}
```

---

## 6. BASE DE DATOS

### Archivo: `backend_python/database/schema.sql`
```sql
-- Habilitar extensión PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabla de fotografías históricas
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    year INTEGER,
    year_from INTEGER,
    year_to INTEGER,
    era VARCHAR(50),
    zone VARCHAR(100),
    lat DECIMAL(10, 8) NOT NULL,
    lng DECIMAL(11, 8) NOT NULL,
    geometry GEOMETRY(Point, 4326),
    image_url VARCHAR(500) NOT NULL,
    thumb_url VARCHAR(500) NOT NULL,
    source VARCHAR(255),
    author VARCHAR(255),
    rights VARCHAR(255),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice espacial GIST
CREATE INDEX IF NOT EXISTS idx_photos_geometry ON photos USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_photos_year ON photos(year);
CREATE INDEX IF NOT EXISTS idx_photos_era ON photos(era);
CREATE INDEX IF NOT EXISTS idx_photos_zone ON photos(zone);
CREATE INDEX IF NOT EXISTS idx_photos_created_at ON photos(created_at DESC);

-- Trigger: sincronizar lat/lng con geometry automáticamente
CREATE OR REPLACE FUNCTION sync_geometry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geometry = ST_SetSRID(ST_MakePoint(NEW.lng, NEW.lat), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_geometry
    BEFORE INSERT OR UPDATE ON photos
    FOR EACH ROW EXECUTE FUNCTION sync_geometry();

-- Trigger: auto-update de updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_updated_at
    BEFORE UPDATE ON photos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Tabla de capas históricas del mapa
CREATE TABLE IF NOT EXISTS map_layers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    year INTEGER,
    type VARCHAR(20) NOT NULL CHECK (type IN ('plan', 'ortho', 'current')),
    tile_url_template VARCHAR(500),
    attribution TEXT,
    min_zoom INTEGER DEFAULT 10,
    max_zoom INTEGER DEFAULT 19,
    bounds_north DECIMAL(10, 8),
    bounds_south DECIMAL(10, 8),
    bounds_east DECIMAL(11, 8),
    bounds_west DECIMAL(11, 8),
    is_active BOOLEAN DEFAULT true,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_map_layers_year ON map_layers(year);
CREATE INDEX IF NOT EXISTS idx_map_layers_active ON map_layers(is_active);
CREATE INDEX IF NOT EXISTS idx_map_layers_order ON map_layers(display_order);
```

### Datos de ejemplo (seeds.sql) - 8 fotos históricas:

| ID | Título | Año | Zona | Coordenadas |
|----|--------|-----|------|-------------|
| 1 | Plaza del Pilar con el Tranvía | 1935 | Casco Histórico | 41.656648, -0.878611 |
| 2 | Puente de Piedra en construcción | 1948 | Casco Histórico | 41.658333, -0.879722 |
| 3 | Mercado Central en día de mercado | 1952 | Centro | 41.652500, -0.887222 |
| 4 | Paseo Independencia nevado | 1963 | Centro | 41.650833, -0.889444 |
| 5 | Antigua Estación del Norte | 1928 | Delicias | 41.647222, -0.912778 |
| 6 | Feria de Muestras en el Parque | 1941 | Parque Grande | 41.632778, -0.902500 |
| 7 | Universidad y Paraninfo | 1968 | Universidad | 41.644167, -0.893611 |
| 8 | Aljafería vista desde el exterior | 1975 | Romareda | 41.656944, -0.897500 |

### 3 capas de mapa:
1. **Mapa Actual** (OpenStreetMap) - tipo: `current`
2. **Plano histórico 1935** - tipo: `plan` (placeholder, sin tiles)
3. **Ortofoto histórica 1960** - tipo: `ortho` (placeholder, sin tiles)

---

## 7. DOCKER-COMPOSE

```yaml
services:
  postgres:
    image: postgis/postgis:15-3.4
    container_name: zaragoza_historica_db
    environment:
      POSTGRES_USER: zaragoza_user
      POSTGRES_PASSWORD: zaragoza_pass
      POSTGRES_DB: zaragoza_historica
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend_python/database:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U zaragoza_user -d zaragoza_historica"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - zaragoza_network

  backend:
    build:
      context: ./backend_python
      dockerfile: Dockerfile
    container_name: zaragoza_historica_backend
    environment:
      PORT: 3000
      HOST: 0.0.0.0
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: zaragoza_historica
      DB_USER: zaragoza_user
      DB_PASSWORD: zaragoza_pass
      CORS_ORIGINS: http://localhost:5173,http://localhost:3000
    ports:
      - "3000:3000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend/uploads:/app/uploads
    networks:
      - zaragoza_network
    restart: unless-stopped

networks:
  zaragoza_network:
    driver: bridge

volumes:
  postgres_data:
```

---

## 8. API REST - ENDPOINTS

| Método | Ruta | Descripción | Parámetros |
|--------|------|-------------|------------|
| GET | `/api/health` | Health check | - |
| GET | `/api/photos` | Listar fotos con filtros | `bbox`, `yearFrom`, `yearTo`, `era`, `zone`, `q`, `page`, `pageSize` |
| GET | `/api/photos/{id}` | Detalle de foto por ID | - |
| GET | `/api/photos/metadata/filters` | Metadatos para filtros | - |
| GET | `/api/layers` | Capas del mapa activas | - |
| GET | `/api/layers/{id}` | Capa por ID | - |

### Ejemplo de respuesta GET /api/photos:
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
    }
  ],
  "total": 8,
  "page": 1,
  "pageSize": 20,
  "totalPages": 1
}
```

### Ejemplo GET /api/photos/metadata/filters:
```json
{
  "eras": ["Años 20", "Años 30", "Años 40", "Años 50", "Años 60", "Años 70"],
  "zones": ["Casco Histórico", "Centro", "Delicias", "Parque Grande", "Romareda", "Universidad"],
  "yearRange": { "min": 1928, "max": 1975 }
}
```

---

## 9. VARIABLES DE ENTORNO

```env
# Database
DB_HOST=localhost          # (o "postgres" en Docker)
DB_PORT=5432
DB_NAME=zaragoza_historica
DB_USER=zaragoza_user
DB_PASSWORD=zaragoza_pass

# Server
PORT=3000
HOST=0.0.0.0
DEBUG=false

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 10. CSS COMPLETO (frontend/src/index.css)

Layout de 3 paneles: sidebar izquierda (filtros, 320px) + mapa central (flex) + sidebar derecha (lista, 380px).
Responsive con breakpoints a 1024px y 768px.
Tema con gradiente morado (#667eea → #764ba2) en el header.
Cards de fotos con hover/active, paginación estilizada.
Control de capas con radio buttons posicionado sobre el mapa.

---

## 11. CÓMO EJECUTAR

```powershell
# Opción 1: Script automático
.\start.ps1

# Opción 2: Manual
docker-compose up -d           # BD + Backend
cd frontend; npm run dev       # Frontend en puerto 5173

# URLs:
# Frontend: http://localhost:5173
# Backend API: http://localhost:3000
# Swagger Docs: http://localhost:3000/docs
# Health: http://localhost:3000/api/health
```

---

## 12. ROADMAP / TODO

### Completado (MVP):
- [x] Backend API con PostGIS (Python + FastAPI)
- [x] Filtros combinables (año, época, zona, bbox, texto)
- [x] Paginación y ordenación
- [x] Frontend con mapa Leaflet + clustering
- [x] Panel de filtros dinámico
- [x] Lista de resultados sincronizada con mapa
- [x] Selector de capas históricas
- [x] Sincronización bidireccional mapa ↔ lista
- [x] Debounce en movimientos del mapa
- [x] Responsive design
- [x] Swagger UI automático

### Pendiente (futuras mejoras):
- [ ] Panel admin para subir fotos (CRUD)
- [ ] Autenticación (JWT)
- [ ] Almacenamiento en S3
- [ ] Búsqueda por texto completo (PostgreSQL FTS)
- [ ] Favoritos/colecciones
- [ ] Compartir enlaces con filtros
- [ ] Export a PDF/KML
- [ ] PWA / modo offline
- [ ] Tests unitarios e integración
- [ ] CI/CD con GitHub Actions
- [ ] Deploy a producción

---

## 13. NOTAS IMPORTANTES

- El backend fue **migrado de TypeScript/Node.js a Python/FastAPI** el 16 de febrero de 2026. La carpeta `backend/` es el antiguo backend (deprecado), el activo es `backend_python/`.
- Las fotografías históricas son **ficticias** (datos de ejemplo para el TFG), pero las coordenadas son reales de Zaragoza.
- Las capas históricas (plano 1935, ortofoto 1960) son **placeholders** sin tiles reales.
- El directorio `uploads/` sirve para almacenar imágenes localmente.
- El frontend usa un **proxy de Vite** que redirige `/api` → `http://localhost:3000`.
- El pool de conexiones PostgreSQL usa `psycopg2` con `RealDictCursor` para resultados como diccionarios.
- Los queries PostGIS usan `ST_Intersects` con `ST_MakeEnvelope` para filtrado geográfico (bbox).
- El trigger `sync_geometry` convierte automáticamente `lat/lng` a `geometry` Point en cada INSERT/UPDATE.
