"""This module implements testing utility using SQLAlchemy."""

from typing import TYPE_CHECKING

from radikopodcast import Session
from radikopodcast.database.models import Base
from tests.testlibraries.database_engine_manager import DatabaseEngineManager

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy.orm.session import Session as SQLAlchemySession


class DatabaseForTest:
    """This class implements methods about database for unit testing."""

    @classmethod
    def database_session(cls) -> "Generator[SQLAlchemySession, None, None]":
        """This fixture prepares database session to reset database after each test."""
        with DatabaseEngineManager(Session):
            yield Session()

    @classmethod
    def database_session_with_schema(cls) -> "Generator[SQLAlchemySession, None, None]":
        """This fixture prepares database session and fixture records to reset database after each test."""
        with DatabaseEngineManager(Session) as engine:
            session = Session()
            Base.metadata.create_all(engine, checkfirst=False)
            yield session
