from app.core.exceptions import UserAlreadyExistsException
from app.core.uow import SqlAlchemyUnitOfWork
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, uow: SqlAlchemyUnitOfWork):
        self.uow = uow

    async def create_new_user(self, user: UserCreate) -> User:

        async with self.uow:
            # Check if user already exists
            existing_user = await self.uow.users.get_user_by_email(user.email)

            if existing_user is not None:
                raise UserAlreadyExistsException()

            user_data = user.model_dump()
            db_user = User(**user_data)

            new_user = await self.uow.users.add_user(db_user)

            await self.uow.commit()

            return new_user
