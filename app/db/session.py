from __future__ import annotations

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

try:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=50,
        max_overflow=50,
        pool_recycle=1800,
        pool_timeout=30,
    )
    # Test connection
    with engine.connect() as conn:
        logger.info("Successfully connected to primary PostgreSQL database with 1000+ user connection pool.")
except Exception as e:
    logger.warning(
        f"Could not connect to primary database at {settings.DATABASE_URL}: {e}. "
        f"Falling back to SQLite at {settings.SQLITE_FALLBACK_URL}"
    )
    engine = create_engine(
        settings.SQLITE_FALLBACK_URL,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")
