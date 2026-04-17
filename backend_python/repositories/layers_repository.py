"""
Repository para capas del mapa
"""
from typing import List, Optional
from config.database import Database


_BASE_COLUMNS = """
    id, name, year, type, tile_url_template, attribution,
    min_zoom, max_zoom,
    bounds_north, bounds_south, bounds_east, bounds_west,
    is_active, display_order
"""

_BOUND_KEYS = ('bounds_north', 'bounds_south', 'bounds_east', 'bounds_west')


def _format_layer(row) -> dict:
    """Convierte una fila en dict y colapsa bounds_* en sub-objeto bounds."""
    layer = dict(row)
    if layer.get('bounds_north') is not None:
        layer['bounds'] = {
            'north': layer['bounds_north'],
            'south': layer['bounds_south'],
            'east': layer['bounds_east'],
            'west': layer['bounds_west'],
        }
    else:
        layer['bounds'] = None
    for key in _BOUND_KEYS:
        layer.pop(key, None)
    return layer


class LayersRepository:
    """Repository para acceso a datos de capas"""

    def find_all(self) -> List[dict]:
        query = f"""
            SELECT {_BASE_COLUMNS}
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
            return [_format_layer(row) for row in results]
        finally:
            Database.return_connection(conn)

    def find_by_id(self, layer_id: int) -> Optional[dict]:
        query = f"""
            SELECT {_BASE_COLUMNS}
            FROM map_layers
            WHERE id = %s
        """
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, (layer_id,))
            row = cursor.fetchone()
            cursor.close()
            return _format_layer(row) if row else None
        finally:
            Database.return_connection(conn)


# Singleton
layers_repository = LayersRepository()
