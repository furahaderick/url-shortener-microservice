from app.exceptions import UserAlreadyExistsException
from app.repositories.interfaces import UserRepository
from app.schemas.user import UserCreate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_new_user(self, user: UserCreate):
        # Check if user already exists
        existing_user = await self.repo.get_user_by_email(user.email)

        if existing_user is not None:
            raise UserAlreadyExistsException()

        return await self.repo.add_user(user)
