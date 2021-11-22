"""Top-level package for radiko Podcast."""

__author__ = """Master"""
__email__ = "roadmasternavi@gmail.com"
__version__ = "1.0.1"

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from radikopodcast.config import Config

# pylint: disable=invalid-name
Session = scoped_session(
    sessionmaker(
        bind=create_engine("sqlite:///programs.db"),
        # ↓ @ see https://stackoverflow.com/questions/32922210/why-does-a-query-invoke-a-auto-flush-in-sqlalchemy
        autoflush=False,
        # ↓ To use with-statement
        autocommit=True,
    )
)
CONFIG: Config = Config()
