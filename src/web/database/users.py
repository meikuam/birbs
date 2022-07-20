import contextlib
from typing import AsyncGenerator
from fastapi import Depends

from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

from src.web.models.users import UserRead
from src.web.database.engine.postgres import engine, async_session_maker


Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    # TODO: additional fields are ignored at create_db_and_tables
    pass


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_async_session_context = contextlib.asynccontextmanager(get_async_session)
