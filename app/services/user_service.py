from uuid import UUID

from jwt import PyJWTError

from app.core.exceptions import (
    InvalidCredentialsException,
    InvalidTokenException,
    UserAlreadyExistsException,
)
from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.uow import SqlAlchemyUnitOfWork
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import LoginCredentials, UserCreate


class UserService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self.uow = uow

    async def create_new_user(self, user: UserCreate) -> User:

        async with self.uow:
            # Check if user already exists
            existing_user = await self.uow.users.get_user_by_email(user.email)

            if existing_user is not None:
                raise UserAlreadyExistsException()

            user_data = user.model_dump(exclude={"password"})
            db_user = User(**user_data, password_hash=hash_password(user.password))

            new_user = await self.uow.users.add_user(db_user)

            await self.uow.commit()

            return new_user

    async def login_user(self, credentials: LoginCredentials) -> Token:
        async with self.uow:
            # Check if user exists
            user = await self.uow.users.get_user_by_email(credentials.email)

            if user is None:
                raise InvalidCredentialsException()

            # Verify user's password
            if not verify_password(credentials.password, user.password_hash):
                raise InvalidCredentialsException()

            access_token = create_access_token(subject=user.id, user_tier=user.tier)
            refresh_token = create_refresh_token(subject=user.id)

            return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        async with self.uow:
            try:
                payload = decode_token(refresh_token)

                if payload.get("type") != TokenType.REFRESH:
                    raise InvalidTokenException()

                user_uuid = UUID(payload["sub"])

            except (PyJWTError, KeyError, ValueError, TypeError):
                raise InvalidTokenException()

            user = await self.uow.users.get_user_by_id(user_uuid)

            if user is None:
                raise InvalidTokenException()

            access_token = create_access_token(subject=user.id, user_tier=user.tier)
            refresh_token = create_refresh_token(subject=user.id)

            return Token(access_token=access_token, refresh_token=refresh_token)
