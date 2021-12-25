import os
import databases
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

username = os.getenv('POSTGRES_USER', "postgres")
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
hostname = os.getenv('POSTGRES_HOST', 'postgres')
database_name = os.getenv('POSTGRES_DATABASE', 'birbs_db')
port = os.getenv('POSTGRES_PORT', '8807')

DATABASE_URL = "postgresql+asyncpg://%s:%s@%s:%s/%s" % (username, password, hostname, port, database_name)

database = databases.Database(DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL, echo=True
)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session