"""
Dependencies de autenticación para proteger rutas
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.schemas import TokenData, UserResponse
from services.auth_service import auth_service


# Esquema de seguridad Bearer
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenData:
    """
    Dependency que extrae y valida el token JWT del header Authorization
    Uso: @router.get("/ruta", dependencies=[Depends(get_current_user)])
    O: async def endpoint(user: TokenData = Depends(get_current_user))
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    token = credentials.credentials
    token_data = auth_service.verify_token(token)

    if not token_data:
        raise credentials_exception

    return token_data


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency que obtiene el usuario completo y verifica que esté activo
    """
    user = auth_service.get_current_user_by_token_data(current_user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return user


async def get_admin_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency que verifica que el usuario sea admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    return current_user
