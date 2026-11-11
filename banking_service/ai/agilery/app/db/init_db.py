"""
Database initialization hook.
"""

from sqlmodel import SQLModel

from ai.agilery.app.db.session import engine


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
