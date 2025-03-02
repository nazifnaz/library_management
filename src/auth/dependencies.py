from typing import Any, List, Union

from fastapi import Depends, Request, Header
from fastapi.security import HTTPBearer
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.db.models import User, ApiKey
from src.db.redis import token_in_blocklist
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    UserNotActive, InvalidApiKey,
)
from .services import UserService
from .utils import decode_token, generate_hash_key, ApiKeyEncryption

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request, session: AsyncSession = Depends(get_session)):
        api_key_token = request.headers.get("X-API-Key")
        if api_key_token:
            return await self.verify_api_key(api_key_token, session)
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

    async def verify_api_key(self, token: str, session: AsyncSession):
        hashed_key = generate_hash_key(token)
        result = await session.exec(
            select(ApiKey).where(ApiKey.hashed_key == hashed_key).options(selectinload(ApiKey.user)))
        result = result.first()
        if result and token == ApiKeyEncryption().decrypt_data(result.key):
            return result.user
        raise InvalidApiKey()


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
        x_api_key: str = Header(None),
        token_details: Union[dict, User] = Depends(AccessTokenBearer()),
        session: AsyncSession = Depends(get_session),
):
    if type(token_details) == User:
        return token_details
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
