from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

_hasher = PasswordHash.recommended()


class TokenType(StrEnum):
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"


def hash_password(plain_password: str) -> str:
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _hasher.verify(plain_password, hashed_password)


def _create_token(
    subject: UUID,
    expires_delta: timedelta,
    token_type: TokenType,
    extra_claims: dict | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": now + expires_delta,
        "type": token_type,
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_access_token(subject: UUID, user_tier: str) -> str:
    return _create_token(
        subject=subject,
        expires_delta=timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
        token_type=TokenType.ACCESS,
        extra_claims={"tier": user_tier},
    )


def create_refresh_token(subject: UUID) -> str:
    return _create_token(
        subject=subject,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type=TokenType.REFRESH,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
