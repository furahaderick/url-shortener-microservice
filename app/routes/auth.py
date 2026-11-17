from fastapi import APIRouter, status

from app.core.dependencies import UserServiceDep
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_account(user: UserCreate, user_service: UserServiceDep):
    return await user_service.create_new_user(user)


@router.post("/login", status_code=status.HTTP_200_OK)
def login():
    return {"access_token": "SOME_ACCESS_TOKEN", "refresh_token": "SOME_REFRESH_TOKEN"}


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_access_token():
    return {"access_token": "SOME_ACCESS_TOKEN", "refresh_token": "SOME_REFRESH_TOKEN"}
