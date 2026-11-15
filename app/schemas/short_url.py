from datetime import datetime
import uuid
from pydantic import BaseModel, HttpUrl


class ShortUrlCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: str | None = None
    title: str | None = None
    description: str | None = None
    favicon: str | None = None

    # Receiving owner id thru body for now
    owner_id: uuid.UUID


class ShortUrlUpdate(BaseModel):
    custom_alias: str | None = None
    title: str | None = None
    description: str | None = None
    favicon: str | None = None


class ShortUrlResponse(BaseModel):
    id: uuid.UUID
    original_url: str
    short_code: str
    custom_alias: str | None
    is_active: bool
    expires_at: datetime | None
    title: str | None
    description: str | None
    favicon: str | None
    click_count: int
    owner_id: uuid.UUID

    model_config = {"from_attributes": True}
