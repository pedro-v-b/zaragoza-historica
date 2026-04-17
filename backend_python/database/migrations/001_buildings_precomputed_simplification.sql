-- 2026-04-18: columnas de geometría pre-simplificada para catastro_buildings
-- Objetivo: eliminar el coste de ST_SimplifyPreserveTopology por fila en cada
-- petición del mapa. Se precalcula una vez y se reutiliza en cada SELECT.
--
-- Zooms y tolerancias (coinciden con simplify_for_zoom):
--   z >= 17  → geometría original (no se almacena duplicada)
--   z >= 15  → geom_z15 (tol 0.000010)
--   z >= 13  → geom_z13 (tol 0.000050)
--   z >= 11  → geom_z11 (tol 0.000200)
--
-- Idempotente: se puede re-ejecutar.

BEGIN;

ALTER TABLE catastro_buildings
    ADD COLUMN IF NOT EXISTS geom_z15 GEOMETRY(MultiPolygon, 4326),
    ADD COLUMN IF NOT EXISTS geom_z13 GEOMETRY(MultiPolygon, 4326),
    ADD COLUMN IF NOT EXISTS geom_z11 GEOMETRY(MultiPolygon, 4326);

-- Poblamos solo las filas que aún no tengan valor (permite re-ejecutar).
UPDATE catastro_buildings
   SET geom_z15 = ST_Multi(ST_SimplifyPreserveTopology(geometry, 0.000010))
 WHERE geom_z15 IS NULL;

UPDATE catastro_buildings
   SET geom_z13 = ST_Multi(ST_SimplifyPreserveTopology(geometry, 0.000050))
 WHERE geom_z13 IS NULL;

UPDATE catastro_buildings
   SET geom_z11 = ST_Multi(ST_SimplifyPreserveTopology(geometry, 0.000200))
 WHERE geom_z11 IS NULL;

-- Versión actualizada del selector por zoom. Hace fallback silencioso a la
-- geometría original si la columna precomputada aún no está poblada.
CREATE OR REPLACE FUNCTION simplify_for_zoom_row(
    b catastro_buildings,
    zoom_level INTEGER
) RETURNS GEOMETRY AS $$
BEGIN
    RETURN CASE
        WHEN zoom_level >= 17 THEN b.geometry
        WHEN zoom_level >= 15 THEN COALESCE(b.geom_z15, b.geometry)
        WHEN zoom_level >= 13 THEN COALESCE(b.geom_z13, b.geometry)
        WHEN zoom_level >= 11 THEN COALESCE(b.geom_z11, b.geometry)
        ELSE                       COALESCE(b.geom_z11, b.geometry)
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

INSERT INTO schema_migrations (version)
VALUES ('001_buildings_precomputed_simplification')
ON CONFLICT DO NOTHING;

COMMIT;
