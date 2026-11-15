from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.short_url_repo import SqlAlchemyShortUrlRepo
from app.repositories.user_repo import SqlAlchemyUserRepo


class SqlAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = SqlAlchemyUserRepo(session)
        self.urls = SqlAlchemyShortUrlRepo(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
