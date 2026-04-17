"""
Repository para operaciones sobre fotos históricas con PostGIS
"""
import os
from typing import List, Tuple, Dict, Optional
from config.database import Database

class PhotosRepository:
    """Repository para acceso a datos de fotos"""

    @staticmethod
    def _storage_base_url() -> str:
        return os.getenv("STORAGE_PUBLIC_URL", "").rstrip('/')

    @staticmethod
    def _apply_base_url(photo: dict, base_url: str) -> dict:
        """Prefija URLs relativas (/uploads/...) con el base URL si existe."""
        if not base_url:
            return photo
        for key in ('image_url', 'thumb_url'):
            value = photo.get(key)
            if value and value.startswith('/uploads/'):
                photo[key] = f"{base_url}{value}"
        return photo

    def find_all(self, filters: dict) -> Tuple[List[dict], int]:
        """
        Obtiene fotos con filtros combinados y paginación
        
        Returns:
            Tuple[List[dict], int]: (lista de fotos, total de resultados)
        """
        bbox = filters.get('bbox')
        year_from = filters.get('yearFrom')
        year_to = filters.get('yearTo')
        era = filters.get('era')
        zone = filters.get('zone')
        q = filters.get('q')
        page = filters.get('page', 1)
        page_size = filters.get('pageSize', 20)
        random_order = filters.get('randomOrder', False)
        seed = filters.get('seed')
        
        where_clauses = []
        query_params = []
        
        # Filtro por bounding box (PostGIS)
        if bbox:
            coords = bbox.split(',')
            min_lng, min_lat, max_lng, max_lat = map(float, coords)
            where_clauses.append(
                f"""ST_Intersects(
                    geometry,
                    ST_MakeEnvelope(%s, %s, %s, %s, 4326)
                )"""
            )
            query_params.extend([min_lng, min_lat, max_lng, max_lat])
        
        # Filtro por rango de años
        if year_from is not None:
            where_clauses.append(f"(year >= %s OR year_to >= %s)")
            query_params.extend([year_from, year_from])
        
        if year_to is not None:
            where_clauses.append(f"(year <= %s OR year_from <= %s)")
            query_params.extend([year_to, year_to])
        
        # Filtro por época
        if era:
            where_clauses.append("era = %s")
            query_params.append(era)
        
        # Filtro por zona
        if zone:
            where_clauses.append("zone = %s")
            query_params.append(zone)
        
        # Búsqueda de texto
        if q:
            where_clauses.append(
                """(
                    title ILIKE %s OR 
                    description ILIKE %s OR
                    array_to_string(tags, ' ') ILIKE %s
                )"""
            )
            search_term = f"%{q}%"
            query_params.extend([search_term, search_term, search_term])
        
        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        
        # Contar total
        count_query = f"SELECT COUNT(*) as count FROM photos {where_clause}"
        
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()

            # Ejecutar count
            cursor.execute(count_query, query_params)
            total = cursor.fetchone()['count']

            offset = (page - 1) * page_size
            if random_order:
                seed_str = str(seed) if seed is not None else "0"
                data_query = f"""
                    SELECT
                        id, title, description, year, year_from, year_to, era, zone,
                        lat, lng, image_url, thumb_url, source, author, rights, tags,
                        created_at, updated_at
                    FROM photos
                    {where_clause}
                    ORDER BY md5(id::text || %s)
                    LIMIT %s OFFSET %s
                """
                exec_params = query_params + [seed_str, page_size, offset]
            else:
                data_query = f"""
                    SELECT
                        id, title, description, year, year_from, year_to, era, zone,
                        lat, lng, image_url, thumb_url, source, author, rights, tags,
                        created_at, updated_at
                    FROM photos
                    {where_clause}
                    ORDER BY year DESC NULLS LAST, created_at DESC
                    LIMIT %s OFFSET %s
                """
                exec_params = query_params + [page_size, offset]

            cursor.execute(data_query, exec_params)
            photos = cursor.fetchall()
            cursor.close()

            base_url = self._storage_base_url()
            formatted_photos = [
                self._apply_base_url(dict(photo), base_url) for photo in photos
            ]
            return formatted_photos, total
            
        finally:
            Database.return_connection(conn)
    
    def find_map_points(self, filters: dict, limit: int) -> List[dict]:
        """Proyección ligera para el mapa: solo campos necesarios y sin COUNT."""
        year_from = filters.get('yearFrom')
        year_to = filters.get('yearTo')
        era = filters.get('era')
        zone = filters.get('zone')
        q = filters.get('q')

        where_clauses: List[str] = []
        query_params: List = []

        if year_from is not None:
            where_clauses.append("(year >= %s OR year_to >= %s)")
            query_params.extend([year_from, year_from])
        if year_to is not None:
            where_clauses.append("(year <= %s OR year_from <= %s)")
            query_params.extend([year_to, year_to])
        if era:
            where_clauses.append("era = %s")
            query_params.append(era)
        if zone:
            where_clauses.append("zone = %s")
            query_params.append(zone)
        if q:
            where_clauses.append(
                "(title ILIKE %s OR description ILIKE %s OR array_to_string(tags, ' ') ILIKE %s)"
            )
            term = f"%{q}%"
            query_params.extend([term, term, term])

        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        query = f"""
            SELECT id, title, lat, lng, image_url, thumb_url
            FROM photos
            {where_clause}
            ORDER BY year DESC NULLS LAST, created_at DESC
            LIMIT %s
        """
        query_params.append(limit)

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, query_params)
            rows = cursor.fetchall()
            cursor.close()

            base_url = self._storage_base_url()
            return [self._apply_base_url(dict(r), base_url) for r in rows]
        finally:
            Database.return_connection(conn)

    def find_by_id(self, photo_id: int) -> Optional[dict]:
        """Obtiene una foto por ID"""
        query = """
            SELECT 
                id, title, description, year, year_from, year_to, era, zone,
                lat, lng, image_url, thumb_url, source, author, rights, tags,
                created_at, updated_at
            FROM photos
            WHERE id = %s
        """
        
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (photo_id,))
            photo = cursor.fetchone()
            cursor.close()
            
            if photo:
                return self._apply_base_url(dict(photo), self._storage_base_url())
            return None
            
        finally:
            Database.return_connection(conn)
    
    def get_filter_metadata(self) -> Dict[str, object]:
        """Obtiene épocas, zonas y rango de años en una sola conexión."""
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT DISTINCT era FROM photos WHERE era IS NOT NULL ORDER BY era"
            )
            eras = [row['era'] for row in cursor.fetchall()]

            cursor.execute(
                "SELECT DISTINCT zone FROM photos WHERE zone IS NOT NULL ORDER BY zone"
            )
            zones = [row['zone'] for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT
                    MIN(COALESCE(year, year_from)) AS min_year,
                    MAX(COALESCE(year, year_to))   AS max_year
                FROM photos
                """
            )
            row = cursor.fetchone() or {}
            cursor.close()

            return {
                'eras': eras,
                'zones': zones,
                'yearRange': {
                    'min': row.get('min_year') or 1800,
                    'max': row.get('max_year') or 2024,
                },
            }
        finally:
            Database.return_connection(conn)

    def create(self, data: dict) -> dict:
        """Crea una nueva foto"""
        query = """
            INSERT INTO photos (
                title, description, year, year_from, year_to, era, zone,
                lat, lng, image_url, thumb_url, source, author, rights, tags
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id, title, description, year, year_from, year_to, era, zone,
                lat, lng, image_url, thumb_url, source, author, rights, tags,
                created_at, updated_at
        """

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (
                data['title'],
                data.get('description'),
                data.get('year'),
                data.get('year_from'),
                data.get('year_to'),
                data.get('era'),
                data.get('zone'),
                data['lat'],
                data['lng'],
                data['image_url'],
                data['thumb_url'],
                data.get('source'),
                data.get('author'),
                data.get('rights'),
                data.get('tags'),
            ))
            photo = cursor.fetchone()
            conn.commit()
            cursor.close()

            return dict(photo)

        finally:
            Database.return_connection(conn)

    def update(self, photo_id: int, data: dict) -> Optional[dict]:
        """Actualiza una foto existente"""
        # Construir query dinámico solo con campos proporcionados
        fields = []
        values = []

        field_mapping = {
            'title': 'title',
            'description': 'description',
            'year': 'year',
            'year_from': 'year_from',
            'year_to': 'year_to',
            'era': 'era',
            'zone': 'zone',
            'lat': 'lat',
            'lng': 'lng',
            'image_url': 'image_url',
            'thumb_url': 'thumb_url',
            'source': 'source',
            'author': 'author',
            'rights': 'rights',
            'tags': 'tags',
        }

        for key, column in field_mapping.items():
            if key in data:
                fields.append(f"{column} = %s")
                values.append(data[key])

        if not fields:
            return self.find_by_id(photo_id)

        values.append(photo_id)

        query = f"""
            UPDATE photos
            SET {', '.join(fields)}
            WHERE id = %s
            RETURNING id, title, description, year, year_from, year_to, era, zone,
                lat, lng, image_url, thumb_url, source, author, rights, tags,
                created_at, updated_at
        """

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, values)
            photo = cursor.fetchone()
            conn.commit()
            cursor.close()

            return dict(photo) if photo else None

        finally:
            Database.return_connection(conn)

    def delete(self, photo_id: int) -> bool:
        """Elimina una foto"""
        query = "DELETE FROM photos WHERE id = %s RETURNING id"

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (photo_id,))
            result = cursor.fetchone()
            conn.commit()
            cursor.close()

            return result is not None

        finally:
            Database.return_connection(conn)


# Singleton
photos_repository = PhotosRepository()
