"""
Dependencies para inyección en FastAPI
"""
from dependencies.auth import get_current_user, get_current_active_user, get_admin_user

__all__ = ["get_current_user", "get_current_active_user", "get_admin_user"]
