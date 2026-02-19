"""
Router para endpoints de capas del mapa
"""
from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import MapLayer
from services.layers_service import layers_service

router = APIRouter(prefix="/layers", tags=["layers"])


@router.get("/{layer_id}", response_model=MapLayer)
async def get_layer_by_id(layer_id: int):
    """Obtiene una capa específica por ID"""
    layer = layers_service.get_layer_by_id(layer_id)
    
    if not layer:
        raise HTTPException(status_code=404, detail=f"Capa con ID {layer_id} no encontrada")
    
    return layer


@router.get("", response_model=List[MapLayer])
async def get_layers():
    """Obtiene todas las capas del mapa activas"""
    return layers_service.get_layers()
