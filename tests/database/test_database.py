# Copyright (C) 2026 Master
"""Tests for database.py."""

import pytest
import sqlalchemy

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
        inspector = sqlalchemy.inspect(engine)
        assert inspector.has_table("stations")
        assert inspector.has_table("programs")

    @staticmethod
    @pytest.mark.usefixtures("legacy_database")
    def test_migrate_database() -> None:
        """Database should add the archive_retry_count column to a pre-upgrade schema."""
        Database()
        engine = Session.get_bind()
        column_names = {column["name"] for column in sqlalchemy.inspect(engine).get_columns("programs")}
        assert "archive_retry_count" in column_names

    @staticmethod
    @pytest.mark.usefixtures("database_session_with_schema")
    def test_migrate_database_idempotent() -> None:
        """Database should be safe to instantiate repeatedly on an up-to-date schema."""
        Database()
        Database()
        engine = Session.get_bind()
        column_names = [column["name"] for column in sqlalchemy.inspect(engine).get_columns("programs")]
        assert column_names.count("archive_retry_count") == 1
