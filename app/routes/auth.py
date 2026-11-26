from fastapi import APIRouter, status

from app.core.dependencies import CurrentUserDep, UserServiceDep
from app.core.rate_limiter import rate_limit
from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.user import LoginCredentials, UserCreate, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_new_account(user: UserCreate, user_service: UserServiceDep):
    return await user_service.create_new_user(user)


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=Token,
    dependencies=[rate_limit(5, seconds=1 * 60)],
)
async def login(credentials: LoginCredentials, user_service: UserServiceDep):
    return await user_service.login_user(credentials=credentials)


@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=Token)
async def refresh_access_token(req: RefreshTokenRequest, user_service: UserServiceDep):
    return await user_service.refresh_access_token(req.refresh_token)


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: CurrentUserDep):
    return current_user
