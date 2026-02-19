# Instalación manual de PostgreSQL + PostGIS (si no usas Docker)

## Opción 1: PostgreSQL con PostGIS en Windows

### 1. Descargar e instalar PostgreSQL
- Descarga desde: https://www.postgresql.org/download/windows/
- Ejecuta el instalador (versión 15 recomendada)
- Durante la instalación:
  - Puerto: 5432
  - Usuario: postgres
  - Contraseña: (elige una y recuérdala)
  - Marca instalar Stack Builder

### 2. Instalar PostGIS
- Al final de la instalación de PostgreSQL, se abre Stack Builder
- Selecciona tu instalación de PostgreSQL 15
- En "Spatial Extensions", selecciona **PostGIS 3.4**
- Completa la instalación

### 3. Crear base de datos
Abre PowerShell o CMD y ejecuta:

```powershell
# Acceder a PostgreSQL
psql -U postgres

# Dentro de psql:
CREATE DATABASE zaragoza_historica;
CREATE USER zaragoza_user WITH PASSWORD 'zaragoza_pass';
GRANT ALL PRIVILEGES ON DATABASE zaragoza_historica TO zaragoza_user;
\q
```

### 4. Ejecutar scripts SQL
```powershell
cd "c:\Users\pvial\Desktop\TFG DAM\backend\database"

# Ejecutar schema
psql -U postgres -d zaragoza_historica -f schema.sql

# Ejecutar seeds
psql -U postgres -d zaragoza_historica -f seeds.sql
```

### 5. Verificar instalación
```powershell
psql -U zaragoza_user -d zaragoza_historica

# Dentro de psql:
SELECT COUNT(*) FROM photos;
SELECT PostGIS_Version();
\q
```

Deberías ver 8 fotos y la versión de PostGIS.

---

## Opción 2: Usar PostgreSQL en WSL2 (Windows Subsystem for Linux)

Si tienes WSL2 instalado:

```bash
# En WSL2 Ubuntu
sudo apt update
sudo apt install postgresql postgresql-contrib postgis

# Iniciar servicio
sudo service postgresql start

# Crear base de datos
sudo -u postgres psql
CREATE DATABASE zaragoza_historica;
CREATE USER zaragoza_user WITH PASSWORD 'zaragoza_pass';
GRANT ALL PRIVILEGES ON DATABASE zaragoza_historica TO zaragoza_user;
\q

# Ejecutar scripts
cd /mnt/c/Users/pvial/Desktop/TFG\ DAM/backend/database
sudo -u postgres psql -d zaragoza_historica -f schema.sql
sudo -u postgres psql -d zaragoza_historica -f seeds.sql
```

---

## Opción 3: PostgreSQL Cloud (desarrollo rápido)

### ElephantSQL (gratis)
1. Regístrate en https://www.elephantsql.com/
2. Crea una instancia gratuita (Tiny Turtle)
3. Copia la URL de conexión
4. Modifica `backend/.env`:
   ```
   DATABASE_URL=postgres://user:pass@servidor.db.elephantsql.com/database
   ```
5. Modifica `backend/src/config/database.ts` para usar DATABASE_URL

### Supabase (gratis)
1. Regístrate en https://supabase.com/
2. Crea un proyecto
3. Ve a Settings → Database → Connection string
4. PostGIS ya viene habilitado
5. Usa la connection string en tu `.env`

---

## ⚡ RECOMENDACIÓN

**Para desarrollo local**: PostgreSQL + PostGIS instalado directamente en Windows es la opción más estable.

**Para prueba rápida**: ElephantSQL o Supabase te permiten empezar inmediatamente sin instalaciones.
