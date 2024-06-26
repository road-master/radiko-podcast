"""Database."""

from logging import getLogger

from sqlalchemy import inspect

from radikopodcast.database.models import Base
from radikopodcast import Session


class Database:
    """Database."""

    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        engine = Session.get_bind()
        inspector = inspect(engine)
        if not inspector.has_table("programs"):
            self.initialize_database()

    @staticmethod
    def initialize_database() -> None:
        """This function create empty tables from SQLAlchemy models."""
        # pylint: disable=no-member
        Base.metadata.create_all(Session.get_bind(), checkfirst=False)
