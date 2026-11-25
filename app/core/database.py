from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# POSTGRES
database_url_obj = URL.create(
    drivername="postgresql+psycopg_async",
    host=settings.PG_HOST,
    username=settings.PG_USER,
    password=settings.PG_PASSWORD,
    port=settings.PG_PORT,
    database=settings.PG_DBNAME,
)

engine = create_async_engine(database_url_obj, echo=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
