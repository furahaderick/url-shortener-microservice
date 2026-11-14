from sqlalchemy import Column, ForeignKey, Table

from app.core.database import Base


short_url_tag_association = Table(
    "short_url_tag_association",
    Base.metadata,
    Column("short_url_id", ForeignKey("short_urls.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
