"""
This module implements testing utility using SQLAlchemy and factory_boy.
@see https://factoryboy.readthedocs.io/en/latest/orms.html#sqlalchemy
"""
from dataclasses import dataclass
from typing import Generator

import factory
from sqlalchemy.orm.session import Session as SQLAlchemySession

from radikopodcast import Session
from radikopodcast.database.models import Base, Program
from radikopodcast.radikoxml.xml_parser import XmlParserProgram
from tests.testlibraries.database_engine_manager import DatabaseEngineManager


# Since factory_boy lacks typing stub.
# Error message: Class cannot subclass "SQLAlchemyModelFactory" (has type "Any")
class ProgramFactory(factory.alchemy.SQLAlchemyModelFactory):  # type: ignore
    """Factory for Store model."""

    class Meta:  # Reason: Model. pylint: disable=too-few-public-methods
        """Settings for factory_boy"""

        model = Program
        sqlalchemy_session = Session


@dataclass
class FixtureRecord:
    """This class implements properties and method to define factory_boy fixture records."""

    interface_program: XmlParserProgram

    def define(self) -> None:
        """This method defines factory_boy fixture records by using properties."""
        ProgramFactory(interface_program=self.interface_program)


class DatabaseForTest:
    """This class implements methods about database for unit testing."""

    @classmethod
    def database_session(cls) -> Generator[SQLAlchemySession, None, None]:
        """This fixture prepares database session to reset database after each test."""
        with DatabaseEngineManager(Session):
            yield Session()

    @classmethod
    def database_session_with_schema(cls) -> Generator[SQLAlchemySession, None, None]:
        """This fixture prepares database session and fixture records to reset database after each test."""
        with DatabaseEngineManager(Session) as engine:
            session = Session()
            Base.metadata.create_all(engine, checkfirst=False)
            yield session
