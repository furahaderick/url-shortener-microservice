import alembic.command
import pytest
import pytest_asyncio
import redis.asyncio as redis
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.redis import RedisContainer

from app.core.database import Base
from app.core.dependencies import get_db, get_redis_client
from app.main import app


# Start Docker containers
@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as container:
        yield container


# Run Alembic migrations
@pytest.fixture(scope="session")
def database_url(postgres):
    # Get a Psycopg 3 connection URL.
    url = postgres.get_connection_url(driver=None)
    db_url = url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1,
    )

    return db_url


@pytest.fixture(scope="session", autouse=True)
def run_migrations(database_url):
    config = Config("alembic.ini")

    config.set_main_option(
        "sqlalchemy.url",
        database_url.replace("%", "%%"),
    )

    alembic.command.upgrade(config, "head")

    return database_url


# Create async database engine
@pytest_asyncio.fixture
async def engine(database_url, run_migrations):
    engine = create_async_engine(
        database_url,
        echo=False,
    )

    yield engine

    await engine.dispose()


# Clean database between tests
@pytest_asyncio.fixture
async def clean_database(engine):
    async with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            await connection.execute(table.delete())


# Create async session
@pytest_asyncio.fixture
async def db_session(engine, clean_database):
    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session


# Create async Redis client
@pytest_asyncio.fixture
async def redis_client(redis_container):
    host = redis_container.get_container_host_ip()
    port = int(redis_container.get_exposed_port(6379))

    client = redis.Redis(
        host=host,
        port=port,
        decode_responses=True,
    )

    await client.flushdb()

    yield client

    await client.flushdb()
    await client.aclose()


# Create async http client
@pytest_asyncio.fixture
async def client(engine, clean_database, redis_client):

    session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    async def override_get_redis():
        return redis_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis_client] = override_get_redis

    async with (
        LifespanManager(app) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test",
        ) as test_client,
    ):
        yield test_client

    app.dependency_overrides.clear()
