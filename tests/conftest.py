# # tests/conftest.py
# import pytest
# import pytest_asyncio
# import asyncio
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from database.models import Base

# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# @pytest_asyncio.fixture(scope="session")
# async def async_engine():
#     engine = create_async_engine(TEST_DATABASE_URL, echo=False)
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield engine
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#     await engine.dispose()

# @pytest_asyncio.fixture
# async def async_session(async_engine):
#     async_session = sessionmaker(
#         async_engine, expire_on_commit=False, class_=AsyncSession
#     )
#     async with async_session() as session:
#         yield session
#         await session.close()

# tests/conftest.py
import pytest
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.models import Base  # Замените на фактический путь к вашему Base

# Set TESTING environment variable if not already set
os.environ["TESTING"] = "TRUE"

from database.engine import get_database_url

TEST_DATABASE_URL = get_database_url()


@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def async_session(async_engine):
    async_session = sessionmaker(
        async_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session
        await session.close()