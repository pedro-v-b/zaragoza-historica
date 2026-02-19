"""
Servicio de lógica de negocio para capas
"""
from typing import List
from models.schemas import MapLayer
from repositories.layers_repository import layers_repository


class LayersService:
    """Servicio de capas con lógica de negocio"""
    
    def get_layers(self) -> List[MapLayer]:
        """Obtiene todas las capas activas"""
        layers_data = layers_repository.find_all()
        return [MapLayer(**layer) for layer in layers_data]
    
    def get_layer_by_id(self, layer_id: int) -> MapLayer:
        """Obtiene una capa por ID"""
        layer_data = layers_repository.find_by_id(layer_id)
        
        if not layer_data:
            return None
        
        return MapLayer(**layer_data)


# Singleton
layers_service = LayersService()
