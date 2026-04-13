"""This module implements SQLAlchemy session life cycle to prevent forgetting close."""

from __future__ import annotations

from contextlib import AbstractContextManager
from typing import TYPE_CHECKING

from sqlalchemy.orm.session import Session as SQLAlchemySession

from radikopodcast import Session

if TYPE_CHECKING:
    from types import TracebackType


class SessionManager(AbstractContextManager[SQLAlchemySession]):
    """This class implements SQLAlchemy session life cycle to prevent forgetting close."""

    def __init__(self) -> None:
        self._session: SQLAlchemySession = Session()

    def __enter__(self) -> SQLAlchemySession:
        return self._session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._session.close()
