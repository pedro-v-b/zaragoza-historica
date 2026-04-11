"""
Repository para operaciones sobre fotos históricas con PostGIS
"""
import os
from typing import List, Tuple, Dict, Optional
from config.database import Database

class PhotosRepository:
    """Repository para acceso a datos de fotos"""
    
    def _format_photo_urls(self, photo: dict) -> dict:
        """Prefija las URLs de las imágenes con el base URL de almacenamiento si existe"""
        base_url = os.getenv("STORAGE_PUBLIC_URL", "").rstrip('/')
        if not base_url:
            return photo
            
        # Solo prefijar si la URL es relativa (empieza por /uploads/)
        for key in ['image_url', 'thumb_url']:
            if photo.get(key) and photo[key].startswith('/uploads/'):
                photo[key] = f"{base_url}{photo[key]}"
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

            # Formatear URLs para cada foto
            formatted_photos = [self._format_photo_urls(dict(photo)) for photo in photos]
            return formatted_photos, total
            
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
                return self._format_photo_urls(dict(photo))
            return None
            
        finally:
            Database.return_connection(conn)
    
    def get_distinct_eras(self) -> List[str]:
        """Obtiene todas las épocas distintas"""
        query = "SELECT DISTINCT era FROM photos WHERE era IS NOT NULL ORDER BY era"
        
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return [row['era'] for row in results]
            
        finally:
            Database.return_connection(conn)
    
    def get_distinct_zones(self) -> List[str]:
        """Obtiene todas las zonas distintas"""
        query = "SELECT DISTINCT zone FROM photos WHERE zone IS NOT NULL ORDER BY zone"
        
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            return [row['zone'] for row in results]
            
        finally:
            Database.return_connection(conn)
    
    def get_year_range(self) -> Dict[str, int]:
        """Obtiene el rango de años disponible"""
        query = """
            SELECT
                MIN(COALESCE(year, year_from)) as min_year,
                MAX(COALESCE(year, year_to)) as max_year
            FROM photos
        """

        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

            return {
                'min': result['min_year'] or 1800,
                'max': result['max_year'] or 2024
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
