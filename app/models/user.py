from enum import StrEnum
import uuid

from sqlalchemy import Boolean, String, Enum as SqlEnum, text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class UserTier(StrEnum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    email: Mapped[str] = mapped_column(String(250), unique=True)

    is_premium: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )

    tier: Mapped[UserTier] = mapped_column(
        SqlEnum(UserTier, values_callable=lambda enum: [e.value for e in enum]),
        default=UserTier.FREE,
        server_default=UserTier.FREE,
    )
