"""
Servicio de lógica de negocio para autenticación
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from models.schemas import TokenData, UserResponse, LoginRequest
from repositories.auth_repository import auth_repository
from config.auth import auth_config


class AuthService:
    """Servicio de autenticación con JWT"""

    # Set para tokens invalidados (logout)
    # En producción usar Redis o base de datos
    _blacklisted_tokens: set = set()

    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """
        Autentica un usuario con username y password
        Returns: datos del usuario si es válido, None si no
        """
        user = auth_repository.find_user_by_username(username)

        if not user:
            return None

        if not auth_repository.verify_password(password, user["password_hash"]):
            return None

        if not user.get("is_active", True):
            return None

        return user

    def create_access_token(self, user_data: dict) -> str:
        """
        Crea un token JWT para el usuario
        """
        expire = datetime.now(timezone.utc) + auth_config.get_token_expiry()

        to_encode = {
            "sub": user_data["username"],
            "user_id": user_data["id"],
            "role": user_data.get("role", "user"),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4())  # Unique token ID para evitar colisiones
        }

        encoded_jwt = jwt.encode(
            to_encode,
            auth_config.SECRET_KEY,
            algorithm=auth_config.ALGORITHM
        )

        return encoded_jwt

    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verifica y decodifica un token JWT
        Returns: TokenData si es válido, None si no
        """
        # Verificar si el token está en la blacklist
        if token in self._blacklisted_tokens:
            return None

        try:
            payload = jwt.decode(
                token,
                auth_config.SECRET_KEY,
                algorithms=[auth_config.ALGORITHM]
            )

            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            role: str = payload.get("role", "user")

            if username is None or user_id is None:
                return None

            return TokenData(
                username=username,
                user_id=user_id,
                role=role
            )

        except JWTError:
            return None

    def logout(self, token: str) -> bool:
        """
        Invalida un token añadiéndolo a la blacklist
        """
        self._blacklisted_tokens.add(token)
        return True

    def get_current_user(self, token: str) -> Optional[UserResponse]:
        """
        Obtiene el usuario actual a partir del token
        """
        token_data = self.verify_token(token)

        if not token_data:
            return None

        user = auth_repository.find_user_by_username(token_data.username)

        if not user:
            return None

        return UserResponse(
            id=user["id"],
            username=user["username"],
            role=user["role"],
            is_active=user["is_active"]
        )

    def get_current_user_by_token_data(self, token_data: TokenData) -> Optional[UserResponse]:
        """
        Obtiene el usuario a partir de TokenData ya verificado
        """
        user = auth_repository.find_user_by_username(token_data.username)

        if not user:
            return None

        return UserResponse(
            id=user["id"],
            username=user["username"],
            role=user["role"],
            is_active=user["is_active"]
        )

    def login(self, login_data: LoginRequest) -> Optional[dict]:
        """
        Proceso completo de login
        Returns: dict con token y datos del usuario, o None si falla
        """
        user = self.authenticate_user(login_data.username, login_data.password)

        if not user:
            return None

        access_token = self.create_access_token(user)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(
                id=user["id"],
                username=user["username"],
                role=user["role"],
                is_active=user["is_active"]
            )
        }


# Singleton
auth_service = AuthService()
