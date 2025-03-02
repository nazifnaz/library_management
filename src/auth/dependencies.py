from typing import Any, List

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User, ApiKey
from src.db.redis import token_in_blocklist

from .services import UserService
from .utils import decode_token, ApiKeyEncryption
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    UserNotActive, InvalidApiKey,
)

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, session: AsyncSession=Depends(get_session)) -> HTTPAuthorizationCredentials | None:
        api_key_token = request.headers.get("X-API-Key")
        if api_key_token:
            token_data = self.verify_api_key(api_key_token, session)
        else:
            creds = await super().__call__(request)

            token = creds.credentials

            token_data = decode_token(token)

            if not self.token_valid(token):
                raise InvalidToken()

            if await token_in_blocklist(token_data["jti"]):
                raise InvalidToken()

            self.verify_token_data(token_data)

            return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")

    def verify_api_key(self, token:str, session: AsyncSession) -> dict:
        encrypted_key = ApiKeyEncryption().encrypt_data(token)
        result = await session.exec(select(ApiKey).where(ApiKey.key == encrypted_key))
        result = result.first()
        if result is None:
            raise InvalidApiKey()
        return {"user": {"email": result.user.email}}


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]

    user = await user_service.get_user_by_email(user_email, session)

    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        if not current_user.is_active:
            raise UserNotActive()
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
