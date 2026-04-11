# 🚀 Guía de Inicio Rápido - Zaragoza Histórica

Esta guía te ayudará a poner en marcha la aplicación en **menos de 5 minutos**.

---

## ⚡ Inicio automático (Windows)

### Opción 1: Script de inicio (MÁS FÁCIL)

1. **Asegúrate de tener Docker Desktop corriendo** (icono en la barra de tareas)
2. Haz doble clic en `start.ps1` o ejecuta en PowerShell:
   ```powershell
   .\start.ps1
   ```
3. ¡Listo! Se abrirá automáticamente el navegador en http://localhost:5173

Para detener todo:
```powershell
.\stop.ps1
```

---

## 🔧 Inicio manual (paso a paso)

### 1️⃣ Iniciar base de datos

Abre PowerShell en la carpeta del proyecto:

```powershell
cd "c:\Users\pvial\Desktop\TFG DAM"
docker-compose up -d
```

**Si Docker falla**: Consulta `INSTALL_POSTGRES.md` para instalar PostgreSQL manualmente.

Verifica que funciona:
```powershell
docker-compose ps
```

Deberías ver `zaragoza_historica_db` con estado `Up`.

---

### 2️⃣ Iniciar Backend

Abre una nueva terminal PowerShell:

```powershell
cd "c:\Users\pvial\Desktop\TFG DAM\backend"
npm run dev
```

Verás algo como:
```
✅ Conectado a PostgreSQL
🚀 Servidor Zaragoza Histórica iniciado
📍 URL: http://localhost:3000
```

Prueba que funciona:
- Abre http://localhost:3000/api/health en tu navegador
- Deberías ver: `{"status":"ok","timestamp":"..."}`

---

### 3️⃣ Iniciar Frontend

Abre **otra** terminal PowerShell (no cierres la anterior):

```powershell
cd "c:\Users\pvial\Desktop\TFG DAM\frontend"
npm run dev
```

Verás:
```
VITE v5.x.x ready in xxx ms
➜ Local: http://localhost:5173/
```

---

### 4️⃣ Abrir en el navegador

Ve a: **http://localhost:5173**

Deberías ver:
- 🗺️ Un mapa de Zaragoza centrado en la Plaza del Pilar
- 📷 8 marcadores con fotos históricas
- 📋 Panel izquierdo con filtros
- 📄 Panel derecho con lista de fotos

---

## ✅ Verificación completa

### Prueba los filtros:

1. **Filtro por año**: Pon "Desde: 1930" y "Hasta: 1950" → Aplicar filtros
2. **Filtro por época**: Selecciona "Años 50"
3. **Filtro por zona**: Selecciona "Casco Histórico"
4. **Solo fotos en pantalla**: Marca el checkbox y mueve el mapa

### Prueba el mapa:

1. **Haz zoom** con la rueda del ratón
2. **Haz clic en un marcador** → Se abre un popup con la foto
3. **Mueve el mapa** → La lista se actualiza automáticamente (con debounce)

### Prueba la lista:

1. **Haz clic en una foto de la lista** → El mapa se centra en esa foto
2. **Navega entre páginas** con los botones de paginación

### Prueba el selector de capas:

1. **Arriba a la derecha** del mapa verás "🗺️ Capas del mapa"
2. Selecciona diferentes capas (las marcadas con 📌 son placeholders)

---

## 🐛 Solución de problemas

### ❌ Error: "Cannot connect to database"

**Problema**: PostgreSQL no está corriendo.

**Solución**:
```powershell
docker-compose up -d
# Espera 10 segundos
docker-compose ps
```

Si sigue fallando, consulta `INSTALL_POSTGRES.md`.

---

### ❌ Error: "Port 3000 already in use"

**Problema**: Ya hay algo corriendo en el puerto 3000.

**Solución**:
```powershell
# Buscar qué proceso usa el puerto 3000
netstat -ano | findstr :3000

# Matar el proceso (reemplaza PID con el número que aparece)
taskkill /PID <PID> /F
```

---

### ❌ Error: "Port 5173 already in use"

**Problema**: Ya hay algo corriendo en el puerto 5173.

**Solución**: Igual que arriba, pero con 5173.

---

### ❌ No aparecen fotos en el mapa

**Problema**: La base de datos está vacía.

**Solución**:
```powershell
# Conectarse a la BD y ejecutar seeds
docker exec -it zaragoza_historica_db psql -U zaragoza_user -d zaragoza_historica -f /docker-entrypoint-initdb.d/seeds.sql
```

---

### ❌ Las imágenes no cargan (placeholder)

**Normal**: Las imágenes en `backend/uploads/` son placeholders.

Para desarrollo, las URLs en `seeds.sql` apuntan a `/uploads/nombre.jpg` que no existen.

**Solución temporal**: Las miniaturas mostrarán un placeholder "Sin imagen".

**Para producción**: Sube imágenes reales a `backend/uploads/` y `backend/uploads/thumbs/`.

---

## 📊 Endpoints de la API

Puedes probar directamente los endpoints:

### Health check
```
GET http://localhost:3000/api/health
```

### Obtener todas las fotos
```
GET http://localhost:3000/api/photos
```

### Filtrar por año
```
GET http://localhost:3000/api/photos?yearFrom=1930&yearTo=1960
```

### Filtrar por zona
```
GET http://localhost:3000/api/photos?zone=Casco%20Histórico
```

### Filtrar por bbox (bounding box)
```
GET http://localhost:3000/api/photos?bbox=-0.9,41.6,-0.8,41.7
```

### Obtener metadatos (épocas, zonas disponibles)
```
GET http://localhost:3000/api/photos/metadata/filters
```

### Obtener capas del mapa
```
GET http://localhost:3000/api/layers
```

---

## 📚 Siguiente paso

Una vez que todo funciona:

1. **Añade fotos reales**: Edita `backend/database/seeds.sql` o usa el panel admin (futuro)
2. **Configura capas históricas**: Añade tiles georeferenciados en `map_layers`
3. **Personaliza filtros**: Modifica `frontend/src/components/Filters/Filters.tsx`
4. **Despliega**: Sigue las instrucciones en `README.md` sección "Deploy"

---

## 🎉 ¡Disfruta desarrollando!

Si todo funciona, tienes un **MVP completo** de Zaragoza Histórica con:
- ✅ Mapa interactivo con clustering
- ✅ Filtros avanzados combinables
- ✅ Sincronización bidireccional
- ✅ API REST con PostGIS
- ✅ Paginación y búsqueda
- ✅ Selector de capas históricas

**Documenta tu trabajo para el TFG** 📝
