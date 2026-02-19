# Backend Python - Zaragoza Histórica

Backend en Python con FastAPI para la aplicación Zaragoza Histórica.

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

### Desarrollo Local

1. **Crear entorno virtual**:
```bash
cd backend_python
python -m venv venv
```

2. **Activar entorno virtual**:
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. **Iniciar servidor de desarrollo**:
```bash
python main.py
```

El servidor estará disponible en:
- API: http://localhost:3000/api
- Documentación interactiva: http://localhost:3000/docs
- Health check: http://localhost:3000/api/health

## 📁 Estructura

```
backend_python/
├── main.py                     # Punto de entrada de FastAPI
├── requirements.txt            # Dependencias de Python
├── Dockerfile                  # Contenedor Docker
├── .env.example                # Plantilla de variables de entorno
├── config/
│   └── database.py            # Configuración PostgreSQL
├── models/
│   └── schemas.py             # Modelos Pydantic
├── repositories/
│   ├── photos_repository.py   # Acceso a datos de fotos
│   └── layers_repository.py   # Acceso a datos de capas
├── services/
│   ├── photos_service.py      # Lógica de negocio fotos
│   └── layers_service.py      # Lógica de negocio capas
└── routers/
    ├── photos.py              # Endpoints de fotos
    └── layers.py              # Endpoints de capas
```

## 🛠️ Stack Tecnológico

- **FastAPI**: Framework web moderno y rápido
- **Pydantic**: Validación de datos y serialización
- **psycopg2**: Driver PostgreSQL
- **Uvicorn**: Servidor ASGI de alto rendimiento

## 📚 API Endpoints

### Photos
- `GET /api/photos` - Lista de fotos con filtros
- `GET /api/photos/{id}` - Foto específica
- `GET /api/photos/metadata/filters` - Metadatos para filtros

### Layers
- `GET /api/layers` - Lista de capas del mapa
- `GET /api/layers/{id}` - Capa específica

### Health
- `GET /api/health` - Estado de la API

Ver documentación completa en: http://localhost:3000/docs

## 🔧 Variables de Entorno

```env
# Database
DB_HOST=localhost
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

## 🐛 Debugging

Para ejecutar en modo debug:
```bash
# En .env
DEBUG=true

# Ejecutar
python main.py
```

El modo debug habilita hot-reload automático al guardar cambios.
