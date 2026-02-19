-- Schema para Zaragoza Histórica
-- PostgreSQL 15 + PostGIS 3.4

-- Habilitar extensión PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabla de fotografías históricas
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Información temporal
    year INTEGER, -- Año principal (puede ser aproximado)
    year_from INTEGER, -- Rango: año desde
    year_to INTEGER, -- Rango: año hasta
    era VARCHAR(50), -- Categoría época: "Años 30", "Años 50", "Belle Époque", etc.
    
    -- Información geográfica
    zone VARCHAR(100), -- Barrio/Distrito: "Casco Histórico", "Delicias", "Universidad"
    lat DECIMAL(10, 8) NOT NULL,
    lng DECIMAL(11, 8) NOT NULL,
    geometry GEOMETRY(Point, 4326), -- PostGIS Point con SRID 4326 (WGS84)
    
    -- Archivos
    image_url VARCHAR(500) NOT NULL,
    thumb_url VARCHAR(500) NOT NULL,
    
    -- Metadatos
    source VARCHAR(255), -- Fuente: "Archivo Municipal", "Colección particular"
    author VARCHAR(255), -- Fotógrafo/Autor
    rights VARCHAR(255), -- Derechos: "Dominio público", "Copyright"
    tags TEXT[], -- Array de tags: ['Plaza del Pilar', 'tranvía', 'fiestas']
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índice espacial (GIST) para consultas geográficas rápidas
CREATE INDEX IF NOT EXISTS idx_photos_geometry ON photos USING GIST(geometry);

-- Índices para filtros comunes
CREATE INDEX IF NOT EXISTS idx_photos_year ON photos(year);
CREATE INDEX IF NOT EXISTS idx_photos_era ON photos(era);
CREATE INDEX IF NOT EXISTS idx_photos_zone ON photos(zone);
CREATE INDEX IF NOT EXISTS idx_photos_created_at ON photos(created_at DESC);

-- Trigger para sincronizar lat/lng con geometry
CREATE OR REPLACE FUNCTION sync_geometry()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geometry = ST_SetSRID(ST_MakePoint(NEW.lng, NEW.lat), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_geometry
    BEFORE INSERT OR UPDATE ON photos
    FOR EACH ROW
    EXECUTE FUNCTION sync_geometry();

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_updated_at
    BEFORE UPDATE ON photos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Tabla de capas históricas del mapa
CREATE TABLE IF NOT EXISTS map_layers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    year INTEGER, -- Año del plano/ortofoto
    type VARCHAR(20) NOT NULL CHECK (type IN ('plan', 'ortho', 'current')),
    tile_url_template VARCHAR(500), -- URL de tiles: {z}/{x}/{y}
    attribution TEXT,
    min_zoom INTEGER DEFAULT 10,
    max_zoom INTEGER DEFAULT 19,
    bounds_north DECIMAL(10, 8), -- Bounding box opcional
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
