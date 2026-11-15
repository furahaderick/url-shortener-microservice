from app.core.uow import SqlAlchemyUnitOfWork
from app.exceptions import UserAlreadyExistsException
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self.uow = uow

    async def create_new_user(self, user: UserCreate):

        async with self.uow:
            # Check if user already exists
            existing_user = await self.uow.users.get_user_by_email(user.email)

            if existing_user is not None:
                raise UserAlreadyExistsException()

            new_user = await self.uow.users.add_user(user)

            await self.uow.commit()

            return new_user
