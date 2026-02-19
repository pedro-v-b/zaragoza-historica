"""
Repository para capas del mapa
"""
from typing import List, Optional
from config.database import Database


class LayersRepository:
    """Repository para acceso a datos de capas"""
    
    def find_all(self) -> List[dict]:
        """Obtiene todas las capas activas ordenadas"""
        query = """
            SELECT 
                id, name, year, type, tile_url_template, attribution,
                min_zoom, max_zoom, 
                bounds_north, bounds_south, bounds_east, bounds_west,
                is_active, display_order
            FROM map_layers
            WHERE is_active = true
            ORDER BY display_order ASC
        """
        
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            # Transformar resultados
            layers = []
            for row in results:
                layer = dict(row)
                
                # Construir objeto bounds si existen coordenadas
                if layer.get('bounds_north') is not None:
                    layer['bounds'] = {
                        'north': layer['bounds_north'],
                        'south': layer['bounds_south'],
                        'east': layer['bounds_east'],
                        'west': layer['bounds_west']
                    }
                else:
                    layer['bounds'] = None
                
                # Limpiar campos temporales
                for key in ['bounds_north', 'bounds_south', 'bounds_east', 'bounds_west']:
                    layer.pop(key, None)
                
                layers.append(layer)
            
            return layers
            
        finally:
            Database.return_connection(conn)
    
    def find_by_id(self, layer_id: int) -> Optional[dict]:
        """Obtiene una capa por ID"""
        query = """
            SELECT 
                id, name, year, type, tile_url_template, attribution,
                min_zoom, max_zoom,
                bounds_north, bounds_south, bounds_east, bounds_west,
                is_active, display_order
            FROM map_layers
            WHERE id = %s
        """
        
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (layer_id,))
            row = cursor.fetchone()
            cursor.close()
            
            if not row:
                return None
            
            layer = dict(row)
            
            # Construir objeto bounds si existen coordenadas
            if layer.get('bounds_north') is not None:
                layer['bounds'] = {
                    'north': layer['bounds_north'],
                    'south': layer['bounds_south'],
                    'east': layer['bounds_east'],
                    'west': layer['bounds_west']
                }
            else:
                layer['bounds'] = None
            
            # Limpiar campos temporales
            for key in ['bounds_north', 'bounds_south', 'bounds_east', 'bounds_west']:
                layer.pop(key, None)
            
            return layer
            
        finally:
            Database.return_connection(conn)


# Singleton
layers_repository = LayersRepository()
