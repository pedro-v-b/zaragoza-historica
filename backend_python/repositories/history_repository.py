"""
Repository para contexto histórico anual de Zaragoza
"""
import json
import os
from typing import Optional
from config.database import Database


class HistoryRepository:
    """Repository para acceso a datos de contexto histórico"""

    # Rutas donde buscar el JSON de fallback
    _JSON_PATHS = [
        os.path.join(os.path.dirname(__file__), '..', 'database', 'historical_data.json'),
        r'C:\Users\pvial\Desktop\DATOS_HISTORICOS_ZARAGOZA.json',
    ]

    def find_all(self) -> list:
        """Obtiene todos los registros de contexto histórico ordenados por año"""
        try:
            conn = Database.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT year, alcalde, eventos, noticias_sociedad_sucesos,
                           urbanismo, movilidad_transporte
                    FROM historical_context
                    ORDER BY year ASC
                    """
                )
                rows = cursor.fetchall()
                cursor.close()
                if rows:
                    return [dict(row) for row in rows]
            finally:
                Database.return_connection(conn)
        except Exception:
            pass

        # Fallback: leer desde JSON
        return self._find_all_from_json()

    def _find_all_from_json(self) -> list:
        """Fallback: lee todos los registros del archivo JSON"""
        for path in self._JSON_PATHS:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    result = []
                    for entry in sorted(data, key=lambda x: x.get('año', 0)):
                        result.append({
                            'year': entry['año'],
                            'alcalde': entry.get('alcalde'),
                            'eventos': entry.get('eventos', []),
                            'noticias_sociedad_sucesos': entry.get('noticias_sociedad_sucesos', []),
                            'urbanismo': entry.get('urbanismo', []),
                            'movilidad_transporte': entry.get('movilidad_transporte', []),
                        })
                    return result
                except Exception:
                    continue
        return []

    def find_by_year(self, year: int) -> Optional[dict]:
        """Obtiene el contexto histórico de un año concreto"""
        try:
            conn = Database.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT year, alcalde, eventos, noticias_sociedad_sucesos,
                           urbanismo, movilidad_transporte
                    FROM historical_context
                    WHERE year = %s
                    """,
                    (year,)
                )
                row = cursor.fetchone()
                cursor.close()
                if row:
                    return dict(row)
            finally:
                Database.return_connection(conn)
        except Exception:
            pass

        # Fallback: leer desde JSON si la tabla no existe o está vacía
        return self._find_from_json(year)

    def _find_from_json(self, year: int) -> Optional[dict]:
        """Fallback: busca el año en el archivo JSON"""
        for path in self._JSON_PATHS:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    for entry in data:
                        if entry.get('año') == year:
                            return {
                                'year': entry['año'],
                                'alcalde': entry.get('alcalde'),
                                'eventos': entry.get('eventos', []),
                                'noticias_sociedad_sucesos': entry.get('noticias_sociedad_sucesos', []),
                                'urbanismo': entry.get('urbanismo', []),
                                'movilidad_transporte': entry.get('movilidad_transporte', []),
                            }
                except Exception:
                    continue
        return None


# Singleton
history_repository = HistoryRepository()
