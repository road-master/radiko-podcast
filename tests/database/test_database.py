"""Tests for database.py."""

import pytest
import sqlalchemy

from radikopodcast.database.database import Database
from radikopodcast import Session


class TestDatabase:
    """Tests for Database."""

    @staticmethod
    @pytest.mark.usefixtures("database_session")
    def test() -> None:
        """Database should create tables."""
        Database()
        engine = Session.get_bind()
        inspector = sqlalchemy.inspect(engine)
        assert inspector.has_table("stations")
        assert inspector.has_table("programs")
