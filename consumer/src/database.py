from sqlalchemy import text
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
    pool_size=max(5, settings.DB_POOL_SIZE),
)

asyncSession = sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


# Dependency to get a database session per request
async def get_async_session():
    async with asyncSession() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


# Define an async function to create tables
async def create_tables():
    async with async_engine.begin() as connection:
        await connection.run_sync(BaseModel.metadata.create_all)

# Run the query to create the uuid-ossp extension
async def create_uuid_ossp_extension():
    async with async_engine.begin() as connection:
        await connection.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
