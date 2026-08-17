# Copyright (C) 2026 Master
"""Database."""

from logging import getLogger

from sqlalchemy import inspect
from sqlalchemy import text

from radikopodcast import Session
from radikopodcast.database.models import Base


class Database:
    """Database."""

    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        engine = Session.get_bind()
        if not inspect(engine).has_table("programs"):
            self.initialize_database()
            return
        self.migrate_database()

    @staticmethod
    def initialize_database() -> None:
        """Create empty tables from SQLAlchemy models."""
        # pylint: disable=no-member
        Base.metadata.create_all(Session.get_bind(), checkfirst=False)

    @staticmethod
    def migrate_database() -> None:
        """Add columns introduced after the database file was created."""
        engine = Session.get_bind()
        column_names = {column["name"] for column in inspect(engine).get_columns("programs")}
        if "archive_retry_count" in column_names:
            return
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE programs ADD COLUMN archive_retry_count INTEGER NOT NULL DEFAULT 0"))
