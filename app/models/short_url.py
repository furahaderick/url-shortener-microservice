import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.utils import MAX_CODE_SIZE
from app.models.short_url_tag import short_url_tag_association
from app.models.tag import Tag
from app.models.user import User


class ShortUrl(Base):
    __tablename__ = "short_urls"

    __table_args__ = (UniqueConstraint("short_code", name="uq_short_urls_short_code"),)

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True, default=uuid.uuid4
    )

    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)

    short_code: Mapped[str] = mapped_column(
        String(MAX_CODE_SIZE), index=True, nullable=False
    )

    custom_alias: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true", nullable=False
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    favicon: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    click_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )

    # Relationships
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    owner: Mapped["User"] = relationship()

    tags: Mapped[list["Tag"]] = relationship(
        secondary=short_url_tag_association, lazy="raise"
    )
