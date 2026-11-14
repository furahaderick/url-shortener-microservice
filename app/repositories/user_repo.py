from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.interfaces import UserRepository
from app.schemas.user import UserCreate


class SqlAlchemyUserRepo(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str):
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def add_user(self, user: UserCreate):
        user_data = user.model_dump()
        new_user = User(**user_data)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user
