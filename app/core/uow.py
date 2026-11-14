from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import SqlAlchemyUserRepo


class SqlAlchemyUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = SqlAlchemyUserRepo(session)

    async def __aenter__(self):
        await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.session.rollback()
        else:
            await self.session.commit()
