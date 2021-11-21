"""This module implements database engine manager for unit testing."""
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Optional, Type

import sqlalchemy
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import scoped_session


class DatabaseEngineManager(AbstractContextManager[Engine]):
    """
    This class implements context manager which replaces database engine
    from the one for development / production to the one for unit testing
    to keep data in the development / production database
    and inject new engine on every unit testing to run parallel.
    """

    def __init__(self, argument_scoped_session: scoped_session):
        self.scoped_session = argument_scoped_session
        self.engine = sqlalchemy.create_engine("sqlite://")

    def __enter__(self) -> Engine:
        self.scoped_session.configure(bind=self.engine)
        return self.engine

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        # This comment prevents Pylint duplicate-code.
        traceback: Optional[TracebackType],
    ) -> None:
        # Remove it, so that the next test gets a new Session()
        self.scoped_session.close()
        self.scoped_session.remove()
        self.engine.dispose()
