"""Database engine and session management (async SQLAlchemy)."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

from sqlalchemy.pool import NullPool

# Async engine for FastAPI request handling
engine = create_async_engine(settings.DATABASE_URL, echo=False, poolclass=NullPool)

# Session factory — each request gets its own session
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields a database session per request."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
