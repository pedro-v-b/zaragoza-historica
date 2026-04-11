"""
Router para endpoints de autenticación
"""
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.schemas import LoginRequest, LoginResponse, UserResponse, MessageResponse
from services.auth_service import auth_service
from dependencies.auth import get_current_user, security
from models.schemas import TokenData
from config.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest):
    """
    Autentica un usuario y devuelve un token JWT

    - **username**: nombre de usuario
    - **password**: contraseña
    """
    result = auth_service.login(login_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return LoginResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        user=result["user"]
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Invalida el token JWT actual (logout)

    Requiere: Bearer token en header Authorization
    """
    token = credentials.credentials
    auth_service.logout(token)

    return MessageResponse(
        message="Sesión cerrada correctamente",
        success=True
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Obtiene información del usuario autenticado actual

    Requiere: Bearer token en header Authorization
    """
    token = credentials.credentials
    user = auth_service.get_current_user(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o usuario no encontrado"
        )

    return user
