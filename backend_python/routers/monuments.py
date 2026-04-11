"""
Router para monumentos y patrimonio cultural de Zaragoza.
"""
from fastapi import APIRouter
from services.monuments_service import monuments_service

router = APIRouter(prefix="/monuments", tags=["monuments"])


@router.get("")
async def get_monuments():
    """Devuelve todos los monumentos y patrimonio cultural de Zaragoza."""
    items = monuments_service.get_monuments()
    return {"monuments": items, "total": len(items)}
