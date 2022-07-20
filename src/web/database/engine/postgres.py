from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.utils import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.postgres['user']}:{settings.postgres['password']}@{settings.postgres['host']}:{settings.postgres['port']}/postgres",

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=1,
    echo=True
)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
