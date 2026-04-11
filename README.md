# Zaragoza Histórica 🏛️📷

Aplicación web para visualizar fotografías históricas geolocalizadas de Zaragoza en un mapa interactivo.

**TFG DAM - Trabajo Fin de Grado Desarrollo de Aplicaciones Multiplataforma**

---

## 🎯 Resumen Ejecutivo

**Estado**: ✅ **MVP 100% FUNCIONAL** (Backend Python + Frontend + Base de datos)

**Inicio rápido**: Lee `docs/QUICKSTART.md` o ejecuta `docker-compose up -d`

**Características principales**:
- 🗺️ Mapa interactivo con Leaflet + clustering de marcadores
- 📸 8 fotografías históricas de ejemplo (con coords reales de Zaragoza)
- 🔍 Filtros combinables: año, época, zona, bbox, búsqueda texto
- 🔄 Sincronización bidireccional mapa ↔ lista en tiempo real
- 📄 Paginación de resultados
- 🗂️ Selector de capas históricas (actual + planos/ortofotos)
- 🚀 API REST completa con PostGIS
- 📚 Documentación interactiva automática (Swagger UI)
- 🐍 Backend migrado a Python + FastAPI

**Tech stack**: React + TypeScript + Vite + Leaflet | **Python + FastAPI** + PostgreSQL + PostGIS

**Archivos clave** (todos en `docs/`):
- `docs/QUICKSTART.md` - Guía de inicio en 5 minutos
- `docs/MIGRACION_PYTHON.md` - **Documentación de la migración a Python**
- `docs/API_EXAMPLES.md` - Ejemplos de uso de la API
- `docs/INSTALL_POSTGRES.md` - 3 opciones de instalación de BD
- `docs/RESUMEN.md` - Visión global del proyecto completo
- `docs/GUIA_AÑADIR_FOTOS.md` - Guía para añadir fotos manualmente
- `docs/CONTEXTO_PROYECTO.md` - Contexto y decisiones de diseño

---

## 📋 Características

- 🗺️ Mapa interactivo con Leaflet + clustering de marcadores
- 📸 Fotos históricas geolocalizadas de Zaragoza
- 🔍 Filtros combinables: año, época, zona, bbox
- 🎨 Selector de capas: mapa actual + planos/ortofotos históricas
- 📱 Responsive design
- 🚀 API REST con PostgreSQL + PostGIS

---

## 🛠️ Stack Tecnológico

### Backend
- **Lenguaje**: Python 3.11+
- **Framework**: FastAPI (framework web moderno y rápido)
- **Base de datos**: PostgreSQL 15 + PostGIS 3.4
- **Driver**: psycopg2-binary
- **Validación**: Pydantic
- **Servidor**: Uvicorn (ASGI)
- **Documentación**: Swagger UI automático

### Frontend
- **Framework**: React 18 + TypeScript
- **Build tool**: Vite
- **Mapas**: Leaflet + leaflet.markercluster
- **HTTP Client**: Fetch API

### DevOps
- **Contenedores**: Docker + Docker Compose
- **Variables de entorno**: dotenv

---

## 🚀 Instalación y ejecución

### Requisitos previos
- Node.js 18+ y npm
- Docker y Docker Compose (para la base de datos)

### 1. Clonar repositorio
```bash
cd "c:\Users\pvial\Desktop\TFG DAM"
```

### 2. Iniciar base de datos

**⚠️ IMPORTANTE**: Necesitas PostgreSQL + PostGIS. Elige UNA de estas 3 opciones:

#### Opción A: Docker Compose (RECOMENDADO)
Asegúrate de que Docker Desktop está corriendo, luego:
```powershell
docker-compose up -d
```

Esto iniciará PostgreSQL 15 con PostGIS 3.4 y ejecutará automáticamente:
- `backend/database/schema.sql` - Crea tablas, índices y triggers
- `backend/database/seeds.sql` - Inserta datos de ejemplo (8 fotos)

Verifica que la BD está corriendo:
```powershell
docker-compose ps
```

#### Opción B: PostgreSQL instalado en Windows
Si Docker no funciona, instala PostgreSQL + PostGIS manualmente.
Consulta `docs/INSTALL_POSTGRES.md` para instrucciones detalladas.

#### Opción C: Base de datos en la nube (prueba rápida)
- **ElephantSQL** (gratis): https://www.elephantsql.com/
- **Supabase** (gratis): https://supabase.com/

Luego ejecuta manualmente los scripts SQL en la consola de tu servicio cloud.

### 3. Backend - Instalación y ejecución

```bash
cd backend
npm install
```

Crea el archivo `.env` copiando el ejemplo:
```bash
Copy-Item .env.example .env
```

Inicia el servidor en modo desarrollo:
```bash
npm run dev
```

El backend estará disponible en: **http://localhost:3000**

Endpoints disponibles:
- `GET /api/health` - Health check
- `GET /api/photos` - Listar fotos (con filtros)
- `GET /api/photos/:id` - Detalle de foto
- `GET /api/photos/metadata/filters` - Metadatos para filtros
- `GET /api/layers` - Capas del mapa

### 4. Frontend - Instalación y ejecución

```powershell
cd frontend
npm install
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

**Nota**: El frontend usa un proxy de Vite que redirige `/api` a `http://localhost:3000`, así que asegúrate de que el backend esté corriendo primero.

---

## 📚 Estructura del proyecto

```
TFG DAM/
├── backend/
│   ├── src/
│   │   ├── config/          # Configuración DB
│   │   ├── controllers/     # Controladores HTTP
│   │   ├── services/        # Lógica de negocio
│   │   ├── repositories/    # Acceso a datos
│   │   ├── types/           # TypeScript types
│   │   ├── middlewares/     # Middlewares Express
│   │   ├── routes/          # Rutas API
│   │   └── index.ts         # Entry point
│   ├── database/
│   │   ├── schema.sql       # Schema PostGIS
│   │   └── seeds.sql        # Datos de ejemplo
│   └── uploads/             # Imágenes (local dev)
├── frontend/
│   └── src/
│       ├── components/      # Componentes React
│       ├── services/        # API client
│       ├── types/           # TypeScript types
│       └── hooks/           # Custom hooks
├── docker-compose.yml       # PostgreSQL + PostGIS
└── README.md
```

---

## 🔍 Ejemplos de uso de la API

### Obtener todas las fotos
```bash
curl http://localhost:3000/api/photos
```

### Filtrar por año
```bash
curl "http://localhost:3000/api/photos?yearFrom=1930&yearTo=1960"
```

### Filtrar por época
```bash
curl "http://localhost:3000/api/photos?era=Años%2050"
```

### Filtrar por zona
```bash
curl "http://localhost:3000/api/photos?zone=Casco%20Histórico"
```

### Filtrar por bbox (bounding box visible en el mapa)
```bash
curl "http://localhost:3000/api/photos?bbox=-0.9,-41.6,-0.8,41.7"
```

### Combinar filtros + paginación
```bash
curl "http://localhost:3000/api/photos?yearFrom=1940&zone=Centro&page=1&pageSize=10"
```

### Obtener metadatos para filtros
```bash
curl http://localhost:3000/api/photos/metadata/filters
```

### Obtener capas del mapa
```bash
curl http://localhost:3000/api/layers
```

---

## 🗄️ Modelo de datos

### Tabla `photos`
- Información temporal: `year`, `year_from`, `year_to`, `era`
- Geolocalización: `lat`, `lng`, `geometry` (PostGIS POINT)
- Clasificación: `zone`, `tags`
- Archivos: `image_url`, `thumb_url`
- Metadatos: `source`, `author`, `rights`

### Tabla `map_layers`
- Capas base del mapa: actual, planos históricos, ortofotos
- `tile_url_template` - URL de tiles
- `year`, `type` (plan/ortho/current)
- `bounds` - Límites geográficos opcionales

---

## 📝 TODO / Roadmap

### MVP (Funcional) ✅ COMPLETO
- [x] Backend API con PostGIS
- [x] Filtros combinables (año, época, zona, bbox)
- [x] Paginación y ordenación
- [x] Frontend con mapa Leaflet
- [x] Clustering de marcadores
- [x] Panel de filtros dinámico
- [x] Lista de resultados sincronizada
- [x] Selector de capas históricas
- [x] Sincronización bidireccional mapa ↔ lista
- [x] Debounce en movimientos del mapa
- [x] Responsive design básico

### Futuras mejoras
- [ ] Panel admin para subir fotos
- [ ] Autenticación (JWT)
- [ ] Almacenamiento en S3
- [ ] Búsqueda por texto completo (PostgreSQL FTS)
- [ ] Favoritos/colecciones
- [ ] Compartir enlaces con filtros
- [ ] Export a PDF/KML
- [ ] PWA / modo offline

---

## 👤 Autor

**pvial** - TFG DAM 2025

---

## 📄 Licencia

Este proyecto es un TFG académico. Las fotografías históricas de ejemplo son ficticias.
