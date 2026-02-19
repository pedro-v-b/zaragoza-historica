# 🔄 MIGRACIÓN COMPLETADA: Backend a Python

## ✅ Estado

El backend ha sido **migrado exitosamente de TypeScript/Node.js a Python/FastAPI**.

**Fecha de migración**: 16 de febrero de 2026

---

## 📊 Resumen de la Migración

### Antes (TypeScript)
- **Lenguaje**: TypeScript con Node.js
- **Framework**: Express.js
- **Líneas de código**: ~1,200

### Después (Python)
- **Lenguaje**: Python 3.11+
- **Framework**: FastAPI
- **Líneas de código**: ~900 (más conciso)

---

## 🎯 ¿Qué se mantiene igual?

✅ **Misma funcionalidad exacta**
- Todos los endpoints funcionan igual
- Mismas respuestas JSON
- Mismos filtros y parámetros

✅ **Frontend sin cambios**
- React sigue funcionando sin modificaciones
- La API es 100% compatible

✅ **Base de datos sin cambios**
- PostgreSQL + PostGIS sigue igual
- Mismas tablas y datos

---

## 🚀 ¿Cómo iniciar el proyecto?

### Opción 1: Docker Compose (RECOMENDADO)

```powershell
# Desde la raíz del proyecto
docker-compose up -d
```

Esto iniciará:
- PostgreSQL con PostGIS (puerto 5432)
- Backend Python (puerto 3000)

### Opción 2: Desarrollo local del backend Python

```powershell
# 1. Asegurar que PostgreSQL está corriendo
docker-compose up -d postgres

# 2. Crear entorno virtual (solo primera vez)
cd backend_python
python -m venv venv

# 3. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar .env
cp .env.example .env
# Editar .env si es necesario

# 6. Iniciar servidor
python main.py
```

---

## 📚 Nuevas Características

### 1. Documentación Interactiva Automática

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

Puedes probar todos los endpoints directamente desde el navegador.

### 2. Validación de Datos Mejorada

Pydantic valida automáticamente:
- Tipos de datos
- Valores requeridos vs opcionales
- Rangos numéricos
- Formatos de string

### 3. Mejor Performance

FastAPI es uno de los frameworks más rápidos:
- Basado en Starlette y Pydantic
- Soporte nativo para async/await
- Comparable a Node.js y Go en velocidad

---

## 🗂️ Nueva Estructura del Backend

```
backend_python/
├── main.py                     # Entry point FastAPI
├── requirements.txt            # Dependencias Python
├── Dockerfile                  # Contenedor Python
├── .env                        # Variables de entorno
├── config/
│   └── database.py            # Conexión PostgreSQL
├── models/
│   └── schemas.py             # Modelos Pydantic (validación)
├── repositories/
│   ├── photos_repository.py   # Queries PostgreSQL para fotos
│   └── layers_repository.py   # Queries PostgreSQL para capas
├── services/
│   ├── photos_service.py      # Lógica de negocio fotos
│   └── layers_service.py      # Lógica de negocio capas
└── routers/
    ├── photos.py              # Endpoints de fotos
    └── layers.py              # Endpoints de capas
```

---

## 🔌 Endpoints Disponibles

### Health Check
- `GET /api/health` - Verificar estado de la API

### Photos
- `GET /api/photos` - Lista de fotos con filtros y paginación
- `GET /api/photos/{id}` - Foto específica por ID
- `GET /api/photos/metadata/filters` - Metadatos para filtros

### Layers
- `GET /api/layers` - Lista de capas del mapa
- `GET /api/layers/{id}` - Capa específica por ID

**Ver documentación completa**: http://localhost:3000/docs

---

## 🧪 Probar la API

### Desde PowerShell

```powershell
# Health check
Invoke-WebRequest -Uri http://localhost:3000/api/health -UseBasicParsing

# Listar fotos
Invoke-WebRequest -Uri "http://localhost:3000/api/photos?page=1&pageSize=5" -UseBasicParsing

# Listar capas
Invoke-WebRequest -Uri http://localhost:3000/api/layers -UseBasicParsing
```

### Desde el navegador

Abre http://localhost:3000/docs y prueba los endpoints interactivamente.

---

## ⚙️ Configuración

### Variables de Entorno (.env)

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

---

## 🐛 Resolución de Problemas

### El backend no inicia

```powershell
# Ver logs del contenedor
docker logs zaragoza_historica_backend --tail 50

# Reiniciar contenedor
docker-compose restart backend
```

### Error de conexión a la base de datos

```powershell
# Verificar que PostgreSQL está corriendo
docker-compose ps

# Si no está corriendo, iniciarlo
docker-compose up -d postgres
```

### Reconstruir la imagen del backend

```powershell
# Detener y reconstruir
docker-compose stop backend
docker-compose build backend
docker-compose up -d backend
```

---

## 📖 Archivos de Documentación

- **README.md** - Documentación principal del proyecto
- **backend_python/README.md** - Documentación específica del backend Python
- **QUICKSTART.md** - Guía de inicio rápido
- **API_EXAMPLES.md** - Ejemplos de uso de la API

---

## ✨ Ventajas de Python

1. **Sintaxis más clara y legible** - Menos boilerplate
2. **Type hints nativos** - Similar a TypeScript
3. **Documentación automática** - Swagger UI incluido
4. **Mejor para data science** - Si quieres añadir ML/AI
5. **Gran ecosistema** - Muchas librerías disponibles
6. **PostGIS más natural** - Mejor integración con GeoAlchemy2

---

## 🔄 Backend Antiguo (TypeScript)

El backend antiguo en TypeScript/Node.js está en la carpeta `backend/` y sigue disponible para referencia, pero ya **no se usa**.

Si quisieras volver al backend de Node.js:
1. Editar `docker-compose.yml`
2. Cambiar `context: ./backend_python` a `context: ./backend`
3. Ejecutar `docker-compose up -d --build backend`

---

## 🎉 Conclusión

La migración está **100% completa y probada**. El proyecto ahora usa:

- ✅ **Backend**: Python 3.11 + FastAPI
- ✅ **Frontend**: React + TypeScript (sin cambios)
- ✅ **Base de datos**: PostgreSQL + PostGIS (sin cambios)

**Todo funciona correctamente** y la API mantiene compatibilidad total con el frontend.
