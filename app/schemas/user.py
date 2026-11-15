import uuid

from pydantic import BaseModel, EmailStr

from app.models.user import UserTier


class UserCreate(BaseModel):
    email: EmailStr


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_premium: bool
    tier: UserTier

    model_config = {"from_attributes": True}
