# 📚 Documentación del Proyecto - Zaragoza Histórica

Esta carpeta contiene toda la documentación del proyecto.

## 📖 Documentos Principales

### Para Empezar
- **[README.md](README.md)** - Documentación principal del proyecto
- **[QUICKSTART.md](QUICKSTART.md)** - Guía de inicio rápido (5 minutos)
- **[MIGRACION_PYTHON.md](MIGRACION_PYTHON.md)** - Guía de migración a Python/FastAPI

### Configuración
- **[INSTALL_POSTGRES.md](INSTALL_POSTGRES.md)** - Instalación de PostgreSQL (3 opciones)
- **[docker-compose.yml](../docker-compose.yml)** - Configuración de Docker

### API y Desarrollo
- **[API_EXAMPLES.md](API_EXAMPLES.md)** - Ejemplos de uso de la API REST
- **[backend_python/README.md](../backend_python/README.md)** - Documentación del backend Python
- **API Docs interactiva**: http://localhost:3000/docs (cuando el servidor está corriendo)

### Resumen y Contexto
- **[RESUMEN.md](RESUMEN.md)** - Visión completa del proyecto (estadísticas, arquitectura)
- **[GUIA_AÑADIR_FOTOS.md](GUIA_AÑADIR_FOTOS.md)** - Cómo añadir nuevas fotos a la BD

## 🚀 Stack Tecnológico

- **Backend**: Python 3.11+ con FastAPI
- **Frontend**: React 18 + TypeScript + Vite
- **Base de datos**: PostgreSQL 15 + PostGIS 3.4
- **Mapas**: Leaflet + MarkerCluster
- **DevOps**: Docker + Docker Compose

## 🎯 Inicio Rápido

```powershell
# Iniciar todo el proyecto
.\start.ps1

# O manualmente con Docker
docker-compose up -d
cd frontend
npm run dev
```

## 📞 Soporte

Para problemas o preguntas:
1. Revisa [QUICKSTART.md](QUICKSTART.md) 
2. Revisa [MIGRACION_PYTHON.md](MIGRACION_PYTHON.md) si es un problema del backend
3. Consulta los logs: `docker logs zaragoza_historica_backend`
