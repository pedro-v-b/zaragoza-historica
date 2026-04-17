"""
Repository para consultas de edificios del Catastro.
"""
from typing import List, Optional
from config.database import Database


class BuildingsRepository:
    """Acceso a datos de edificios catastro."""

    def find_geojson_in_bbox(
        self,
        min_lng: float,
        min_lat: float,
        max_lng: float,
        max_lat: float,
        zoom: int = 15,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        limit: int = 5000,
    ) -> dict:
        """Devuelve un FeatureCollection GeoJSON ya construido en Postgres.

        Evita construir el JSON fila-a-fila en Python (json.loads por row) y
        reduce el payload a un único string serializado directamente por PostGIS.
        """
        # ST_Intersects aplica && (bounding box + GiST) internamente.
        conditions = [
            "ST_Intersects(geometry, ST_MakeEnvelope(%s, %s, %s, %s, 4326))",
        ]
        params: list = [
            zoom,
            min_lng, min_lat, max_lng, max_lat,
        ]

        if year_from is not None:
            conditions.append("year_built >= %s")
            params.append(year_from)
        if year_to is not None:
            conditions.append("year_built <= %s")
            params.append(year_to)

        params.append(limit)

        # simplify_for_zoom_row lee columnas precomputadas (geom_z11/z13/z15)
        # y cae a la geometría original si aún no están pobladas.
        query = f"""
            WITH selected AS (
                SELECT
                    id,
                    cadastral_ref,
                    year_built,
                    decade,
                    current_use,
                    simplify_for_zoom_row(catastro_buildings, %s) AS geom
                FROM catastro_buildings
                WHERE {' AND '.join(conditions)}
                ORDER BY year_built
                LIMIT %s
            )
            SELECT COALESCE(
                jsonb_build_object(
                    'type', 'FeatureCollection',
                    'features', COALESCE(
                        jsonb_agg(
                            jsonb_build_object(
                                'type', 'Feature',
                                'geometry', ST_AsGeoJSON(geom)::jsonb,
                                'properties', jsonb_build_object(
                                    'id', id,
                                    'cadastral_ref', cadastral_ref,
                                    'year_built', year_built,
                                    'decade', decade,
                                    'current_use', current_use
                                )
                            )
                        ),
                        '[]'::jsonb
                    )
                ),
                jsonb_build_object('type', 'FeatureCollection', 'features', '[]'::jsonb)
            ) AS fc
            FROM selected
        """

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            cursor.close()
            return row["fc"] if row and row.get("fc") else {
                "type": "FeatureCollection",
                "features": [],
            }
        finally:
            Database.return_connection(conn)

    def get_stats(self) -> dict:
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(year_built) AS with_year,
                    MIN(year_built) AS min_year,
                    MAX(year_built) AS max_year
                FROM catastro_buildings
                """
            )
            summary = dict(cursor.fetchone())

            cursor.execute(
                """
                SELECT decade, COUNT(*) AS count
                FROM catastro_buildings
                WHERE decade IS NOT NULL
                GROUP BY decade
                ORDER BY decade
                """
            )
            by_decade = [dict(row) for row in cursor.fetchall()]
            cursor.close()

            return {
                "total_buildings": summary["total"],
                "with_year": summary["with_year"],
                "year_range": {
                    "min": summary["min_year"],
                    "max": summary["max_year"],
                },
                "by_decade": by_decade,
            }
        finally:
            Database.return_connection(conn)


buildings_repository = BuildingsRepository()
