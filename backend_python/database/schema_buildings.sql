-- ============================================================
-- Esquema de edificios del Catastro Español (INSPIRE GML)
-- Tabla: catastro_buildings
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- NOTA: DROP + CREATE para importación limpia.
-- Si quieres reimportar sin perder datos previos, comenta el DROP.
DROP TABLE IF EXISTS catastro_buildings CASCADE;

CREATE TABLE catastro_buildings (
    id              SERIAL PRIMARY KEY,
    cadastral_ref   VARCHAR(20),
    inspire_id      VARCHAR(100),
    year_built      INTEGER,
    -- decade se calcula automáticamente; no insertar manualmente
    decade          INTEGER GENERATED ALWAYS AS (
                        CASE
                            WHEN year_built IS NOT NULL
                            THEN (year_built / 10) * 10
                        END
                    ) STORED,
    floors_above    SMALLINT,
    floors_below    SMALLINT,
    current_use     VARCHAR(100),
    geometry        GEOMETRY(MultiPolygon, 4326) NOT NULL,
    source          VARCHAR(50)  DEFAULT 'Catastro INSPIRE',
    imported_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- Índice espacial (imprescindible para filtros por bbox)
CREATE INDEX idx_buildings_geometry
    ON catastro_buildings USING GIST(geometry);

-- Índice por año (para filtros de época)
CREATE INDEX idx_buildings_year
    ON catastro_buildings(year_built);

-- Índice por decade (para agrupaciones en estadísticas)
CREATE INDEX idx_buildings_decade
    ON catastro_buildings(decade);

-- Índice espacial parcial para edificios con año (queries mixtas bbox+año)
CREATE INDEX idx_buildings_geom_year
    ON catastro_buildings USING GIST(geometry)
    WHERE year_built IS NOT NULL;

-- ── Función de simplificación adaptativa según zoom ───────────────────────
-- Utilizada por el repository para reducir el payload según el nivel de zoom.
CREATE OR REPLACE FUNCTION simplify_for_zoom(
    geom       GEOMETRY,
    zoom_level INTEGER
) RETURNS GEOMETRY AS $$
BEGIN
    RETURN CASE
        WHEN zoom_level >= 17 THEN geom
        WHEN zoom_level >= 15 THEN ST_SimplifyPreserveTopology(geom, 0.000010)
        WHEN zoom_level >= 13 THEN ST_SimplifyPreserveTopology(geom, 0.000050)
        WHEN zoom_level >= 11 THEN ST_SimplifyPreserveTopology(geom, 0.000200)
        ELSE                       ST_SimplifyPreserveTopology(geom, 0.001000)
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON TABLE catastro_buildings IS
    'Edificios del Catastro Español importados desde el GML INSPIRE';
COMMENT ON COLUMN catastro_buildings.year_built IS
    'Año de construcción extraído del campo bu-core2d:beginning del GML';
COMMENT ON COLUMN catastro_buildings.decade IS
    'Decena calculada automáticamente (ej: 1975 → 1970)';
COMMENT ON COLUMN catastro_buildings.geometry IS
    'Polígono(s) del edificio en WGS84 (EPSG:4326), reproyectado desde ETRS89/UTM30N';
