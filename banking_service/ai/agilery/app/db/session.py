"""
Database session management.
"""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from ai.agilery.app.config.settings import settings

connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)


def get_db() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
