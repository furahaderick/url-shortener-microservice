from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_SUMMARY: str
    APP_BASE_URL: str

    # REDIS Vars
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


settings = Settings()  # type: ignore
