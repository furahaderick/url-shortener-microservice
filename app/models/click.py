import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    city: Mapped[str | None] = mapped_column(String(50), nullable=True)
    country: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user_agent: Mapped[str] = mapped_column(String(100))

    referrer: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Relationships
    short_url_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("short_urls.id", ondelete="CASCADE")
    )
