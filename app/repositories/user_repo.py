from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.interfaces import UserRepository


class SqlAlchemyUserRepo(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_id(self, user_id: UUID):
        return await self.session.get(User, user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def add_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user
