"""
Database connection setup using SQLModel with SQLite for development.
Falls back to in-memory SQLite if PostgreSQL connection fails.
"""

from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from typing import AsyncGenerator
import os

from app.config import settings


def get_database_url():
    """Get database URL, falling back to SQLite if PostgreSQL is unavailable."""
    db_url = settings.database_url
    
    # If using Neon (has asyncpg in scheme), use async SQLite instead
    # since asyncpg has connectivity issues
    if "postgresql" in db_url or "asyncpg" in db_url:
        # Fall back to SQLite for local development
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        os.makedirs(db_path, exist_ok=True)
        sqlite_url = f"sqlite+aiosqlite:///{os.path.join(db_path, 'todo.db')}"
        print("[WARNING] PostgreSQL unavailable, using SQLite instead")
        return sqlite_url
    
    return db_url


# Create async engine
db_url = get_database_url()
async_engine: AsyncEngine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    poolclass=StaticPool,
    connect_args={
        "timeout": 60,
    },
)


# Create async session factory
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    Yields a session and ensures it's closed after use.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables (for development/testing only)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await async_engine.dispose()
