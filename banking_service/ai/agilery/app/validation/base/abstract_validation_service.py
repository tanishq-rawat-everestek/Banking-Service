"""
Base validation service with CRUD lifecycle hooks.
"""

from collections.abc import Callable
from typing import Any, Generic, TypeVar

from ai.agilery.app.db.session import engine
from ai.agilery.app.exception.processing_exception import ProcessingException
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlmodel import Session

D = TypeVar("D")
IdType = TypeVar("IdType")


class AbstractValidationService(Generic[D, IdType]):
    def _execute_read_only(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        session = Session(engine)
        try:
            session.begin()
            session.execute(text("SET TRANSACTION READ ONLY"))
            return func(session, *args, **kwargs)
        except DBAPIError as exc:
            raise ProcessingException("Validation attempted a write operation") from exc
        finally:
            session.close()

    def on_create(self, dto: D) -> None:
        self._execute_read_only(self._validate_create, dto)

    def _validate_create(self, session: Session, dto: D) -> None:
        pass

    def on_update(self, dto: D) -> None:
        self._execute_read_only(self._validate_update, dto)

    def _validate_update(self, session: Session, dto: D) -> None:
        pass

    def on_patch(self, dto: D) -> None:
        self._execute_read_only(self._validate_patch, dto)

    def _validate_patch(self, session: Session, dto: D) -> None:
        pass

    def on_get(self, resource_id: IdType) -> None:
        self._execute_read_only(self._validate_get, resource_id)

    def _validate_get(self, session: Session, resource_id: IdType) -> None:
        pass

    def on_get_all(self, page: int, size: int) -> None:
        self._execute_read_only(self._validate_get_all, page, size)

    def _validate_get_all(self, session: Session, page: int, size: int) -> None:
        pass
