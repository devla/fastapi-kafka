from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from .config import get_settings
from .model import BaseModel

settings = get_settings()


# Create the SQLAlchemy engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=settings.DB_FUTURE,
)


# Define an async function to create tables
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


# Dependency to get a database session
async def get_async_session() -> AsyncSession:
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
