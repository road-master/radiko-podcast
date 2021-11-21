"""This module implements SQLAlchemy session life cycle to prevent forgetting close."""
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Optional, Type

from sqlalchemy.orm.session import Session as SQLAlchemySession

from radikopodcast import Session


class SessionManager(AbstractContextManager[SQLAlchemySession]):
    """
    This class implements SQLAlchemy session life cycle to prevent forgetting close.
    """

    def __init__(self) -> None:
        self._session: SQLAlchemySession = Session()

    def __enter__(self) -> SQLAlchemySession:
        return self._session

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._session.close()
