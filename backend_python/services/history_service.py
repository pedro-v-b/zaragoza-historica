"""
Servicio de lógica de negocio para contexto histórico
"""
from typing import Optional
from models.schemas import HistoricalContext
from repositories.history_repository import history_repository


class HistoryService:
    """Servicio para contexto histórico anual"""

    def get_all(self) -> list:
        """Obtiene todos los registros de contexto histórico"""
        data = history_repository.find_all()
        return [HistoricalContext(**item) for item in data]

    def get_by_year(self, year: int) -> Optional[HistoricalContext]:
        """Obtiene el contexto histórico de un año"""
        data = history_repository.find_by_year(year)
        if not data:
            return None
        return HistoricalContext(**data)


# Singleton
history_service = HistoryService()
