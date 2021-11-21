"""Tests for database.py."""
from typing import cast

import pytest
import sqlalchemy
from sqlalchemy.engine.reflection import Inspector

from radikopodcast import Session
from radikopodcast.database.database import Database


class TestDatabase:
    """Tests for Database."""

    @staticmethod
    @pytest.mark.usefixtures("database_session")
    def test() -> None:
        """Database should create tables."""
        Database()
        engine = Session.get_bind()
        inspector = cast(Inspector, sqlalchemy.inspect(engine))
        assert inspector.has_table("stations")
        assert inspector.has_table("programs")
