"""Database."""
from logging import getLogger
from typing import cast

from sqlalchemy import inspect
from sqlalchemy.engine.reflection import Inspector

from radikopodcast import Session
from radikopodcast.database.models import Base


class Database:
    """Database."""

    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        engine = Session.get_bind()
        inspector = cast(Inspector, inspect(engine))
        if not inspector.has_table("programs"):
            self.initialize_database()

    @staticmethod
    def initialize_database() -> None:
        """This function create empty tables from SQLAlchemy models."""
        # pylint: disable=no-member
        Base.metadata.create_all(Session.get_bind(), checkfirst=False)
