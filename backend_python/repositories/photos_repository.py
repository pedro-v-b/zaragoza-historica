"""
Repository para operaciones sobre fotos históricas con PostGIS
"""
from typing import List, Tuple, Dict, Optional
from config.database import Database


class PhotosRepository:
    """Repository para acceso a datos de fotos"""
    
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
        
        where_clauses = []
        query_params = []
        param_index = 1
        
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
            
            # Query para obtener fotos paginadas
            offset = (page - 1) * page_size
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
            
            cursor.execute(data_query, query_params + [page_size, offset])
            photos = cursor.fetchall()
            
            cursor.close()
            
            return [dict(photo) for photo in photos], total
            
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
            
            return dict(photo) if photo else None
            
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


# Singleton
photos_repository = PhotosRepository()
