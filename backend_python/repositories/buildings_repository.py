"""
Repository para consultas de edificios del Catastro.
"""
from typing import List, Optional
from config.database import Database


class BuildingsRepository:
    """Acceso a datos de edificios catastro."""

    def find_in_bbox(
        self,
        min_lng: float,
        min_lat: float,
        max_lng: float,
        max_lat: float,
        zoom: int = 15,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        limit: int = 5000,
    ) -> List[dict]:
        # ST_Intersects ya aplica && (bounding box + GiST index) internamente.
        conditions = [
            "ST_Intersects(geometry, ST_MakeEnvelope(%s, %s, %s, %s, 4326))",
        ]
        params = [
            zoom,
            min_lng, min_lat, max_lng, max_lat,
        ]

        # Cuando hay filtro de año sólo se muestran edificios con año conocido
        if year_from is not None:
            conditions.append("year_built >= %s")
            params.append(year_from)
        if year_to is not None:
            conditions.append("year_built <= %s")
            params.append(year_to)

        params.append(limit)

        query = f"""
            SELECT
                id,
                cadastral_ref,
                year_built,
                decade,
                current_use,
                ST_AsGeoJSON(simplify_for_zoom(geometry, %s)) AS geojson
            FROM catastro_buildings
            WHERE {' AND '.join(conditions)}
            ORDER BY year_built
            LIMIT %s
        """

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            return [dict(row) for row in rows]
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
