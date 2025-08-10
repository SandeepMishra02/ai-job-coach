# backend/db.py

from __future__ import annotations

from typing import Generator
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./data.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},  # needed for SQLite in single-thread envs
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a DB session."""
    with Session(engine) as session:
        yield session
