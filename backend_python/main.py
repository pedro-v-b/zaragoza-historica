"""
Zaragoza Histórica - Backend API con FastAPI
Aplicación para visualizar fotografías históricas geolocalizadas de Zaragoza
"""
import os
import locale
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional, List

# Configurar locale para usar punto decimal
try:
    locale.setlocale(locale.LC_ALL, 'C')
except Exception:
    pass

# Logging estructurado a nivel raiz
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("zaragoza_historica")

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config.database import Database
from config.rate_limit import limiter
from routers import photos, layers, auth, history, buildings, wikipedia, monuments
from models.schemas import MapPhoto
from services.photos_service import photos_service

# Cargar variables de entorno
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    logger.info("Iniciando Zaragoza Historica API")
    try:
        db_connected = await Database.test_connection()
        if not db_connected:
            logger.warning("Base de datos no disponible")
    except Exception as e:
        logger.warning("No se pudo conectar a la base de datos: %s", e)
    logger.info("API lista para recibir peticiones")
    yield
    logger.info("Cerrando Zaragoza Historica API")
    Database.close_all()
    logger.info("Conexiones cerradas correctamente")


# Crear aplicación FastAPI
app = FastAPI(
    title="Zaragoza Histórica API",
    description="API REST para visualizar fotografías históricas geolocalizadas de Zaragoza",
    version="1.0.0",
    lifespan=lifespan
)

# Rate limiting global (slowapi)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
def get_uploads_path():
    env_path = os.environ.get('UPLOADS_DIR')
    if env_path: return os.path.abspath(env_path)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))

uploads_path = get_uploads_path()
os.makedirs(os.path.abspath(uploads_path), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=os.path.abspath(uploads_path)), name="uploads")


# Endpoint optimizado para el mapa (DIRECTO EN MAIN PARA EVITAR ERRORES DE RUTAS)
@app.get("/api/map", response_model=List[MapPhoto])
async def get_photos_for_map(
    yearFrom: Optional[int] = Query(None),
    yearTo: Optional[int] = Query(None),
    era: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    q: Optional[str] = Query(None)
):
    """Obtiene datos ligeros de todas las fotos para el mapa"""
    filters = {
        'yearFrom': yearFrom, 'yearTo': yearTo, 'era': era, 'zone': zone, 'q': q,
        'page': 1, 'pageSize': 10000 
    }
    photos_data, _ = photos_service.get_photos_raw(filters)
    return [
        MapPhoto(id=p['id'], lat=p['lat'], lng=p['lng'], title=p['title'], image_url=p['image_url'], thumb_url=p['thumb_url']) 
        for p in photos_data
    ]


# Health check endpoint
@app.get("/api/health")
async def health_check():
    return JSONResponse({"status": "ok", "timestamp": datetime.now().isoformat()})


# Incluir routers
app.include_router(auth.router, prefix="/api")
app.include_router(photos.router, prefix="/api")
app.include_router(layers.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(buildings.router, prefix="/api")
app.include_router(wikipedia.router, prefix="/api")
app.include_router(monuments.router, prefix="/api")


# Manejador de 404
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Endpoint no encontrado"})


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 3000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=debug, log_level="info")
