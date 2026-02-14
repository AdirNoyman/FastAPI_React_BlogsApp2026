from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

# Returns a new database session for each request (each request gets her own session). The 'with' statement ensures that the session is properly closed after the request is processed, even if an error occurs. This is important for preventing database connection leaks and ensuring that resources are managed efficiently.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


