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
from routers import photos, layers, auth

# Cargar variables de entorno
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación"""
    # Startup
    print("\n[*] Iniciando Zaragoza Historica API...")

    # Verificar conexión a base de datos (no abortar si falla)
    try:
        db_connected = await Database.test_connection()
        if not db_connected:
            print("[WARN] Base de datos no disponible. Endpoints de fotos/layers no funcionaran.")
    except Exception as e:
        print(f"[WARN] No se pudo conectar a la base de datos: {e}")

    print("[OK] API lista para recibir peticiones\n")
    
    yield
    
    # Shutdown
    print("\n[*] Cerrando Zaragoza Historica API...")
    Database.close_all()
    print("[OK] Conexiones cerradas correctamente\n")


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
    # Crear directorio uploads si no existe
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
app.include_router(auth.router, prefix="/api")
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
    
    print(f"\n[*] Servidor Zaragoza Historica iniciado")
    print(f"    URL: http://localhost:{port}")
    print(f"    API: http://localhost:{port}/api")
    print(f"    Docs: http://localhost:{port}/docs")
    print(f"    Health: http://localhost:{port}/api/health\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
