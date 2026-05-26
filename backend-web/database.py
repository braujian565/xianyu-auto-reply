"""Database connection and session management module.

Handles SQLite/PostgreSQL connections via SQLAlchemy with async support.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import Config
from logger import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Module-level engine and session factory (initialized lazily)
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_database_url(config: Config) -> str:
    """Construct the async database URL from config.

    Falls back to a local SQLite file when no explicit DB URL is provided.
    """
    db_url: str = getattr(config, "DATABASE_URL", "") or ""

    if not db_url:
        db_path = getattr(config, "SQLITE_PATH", "data/xianyu.db")
        db_url = f"sqlite+aiosqlite:///{db_path}"
        logger.debug("No DATABASE_URL set, using SQLite at %s", db_path)
    elif db_url.startswith("postgresql://"):
        # Ensure async driver is used
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+aiomysql://", 1)

    return db_url


def init_engine(config: Config) -> AsyncEngine:
    """Create and return the async SQLAlchemy engine.

    Should be called once at application startup.
    """
    global _engine, _session_factory

    db_url = _build_database_url(config)
    pool_size: int = getattr(config, "DB_POOL_SIZE", 5)
    echo: bool = getattr(config, "DB_ECHO", False)

    logger.info("Initialising database engine (echo=%s)", echo)

    _engine = create_async_engine(
        db_url,
        echo=echo,
        pool_pre_ping=True,
        # SQLite doesn't support connection pooling the same way
        **({"pool_size": pool_size, "max_overflow": 10} if "sqlite" not in db_url else {}),
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    return _engine


async def create_tables() -> None:
    """Create all tables defined in ORM models (idempotent)."""
    if _engine is None:
        raise RuntimeError("Database engine has not been initialised. Call init_engine() first.")

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified.")


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a database session.

    Usage::

        async with get_session() as session:
            result = await session.execute(select(MyModel))
    """
    if _session_factory is None:
        raise RuntimeError("Database engine has not been initialised. Call init_engine() first.")

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def check_connection() -> bool:
    """Ping the database and return True if reachable."""
    try:
        async with get_session() as session:
            await session.execute(text("SELECT 1"))
        logger.debug("Database connection check passed.")
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Database connection check failed: %s", exc)
        return False


async def close_engine() -> None:
    """Dispose the engine and release all connections.

    Should be called during application shutdown.
    """
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database engine closed.")
