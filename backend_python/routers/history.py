"""
Router para endpoints de contexto histórico
"""
from typing import List
from fastapi import APIRouter, HTTPException
from models.schemas import HistoricalContext
from services.history_service import history_service

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=List[HistoricalContext])
async def get_all_historical_context():
    """
    Obtiene el contexto histórico de todos los años disponibles (1900-2025).
    """
    return history_service.get_all()


@router.get("/{year}", response_model=HistoricalContext)
async def get_historical_context(year: int):
    """
    Obtiene el contexto histórico de Zaragoza para un año concreto.
    Rango disponible: 1900-2025.
    """
    if year < 1900 or year > 2025:
        raise HTTPException(
            status_code=400,
            detail=f"Año {year} fuera del rango disponible (1900-2025)"
        )

    context = history_service.get_by_year(year)
    if not context:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos históricos para el año {year}"
        )

    return context
