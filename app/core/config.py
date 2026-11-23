from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_SUMMARY: str
    APP_BASE_URL: str
    APP_DOMAIN: str

    # REDIS Vars
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # POSTGRES Vars
    PG_HOST: str
    PG_USER: str
    PG_PASSWORD: str
    PG_PORT: int
    PG_DBNAME: str

    # SECURITY Vars
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_DAYS: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


settings = Settings()  # type: ignore
