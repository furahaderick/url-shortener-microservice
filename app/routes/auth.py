from fastapi import APIRouter, Depends, status

from app.dependencies import get_user_service
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_account(
    user: UserCreate, user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_new_user(user)


@router.post("/login", status_code=status.HTTP_200_OK)
def login():
    return {"access_token": "SOME_ACCESS_TOKEN", "refresh_token": "SOME_REFRESH_TOKEN"}


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_access_token():
    return {"access_token": "SOME_ACCESS_TOKEN", "refresh_token": "SOME_REFRESH_TOKEN"}
