"""Top-level package for radiko Podcast."""

__author__ = """Master"""
__email__ = "roadmasternavi@gmail.com"
__version__ = "1.2.0"

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from radikopodcast.config import Config

# Reason: To follow the official documentation of SQLAlchemy:
# - Session Basics — SQLAlchemy 2.0 Documentation
#   https://docs.sqlalchemy.org/en/20/orm/session_basics.html
Session = scoped_session(sessionmaker(bind=create_engine("sqlite://")))  # pylint: disable=invalid-name
CONFIG: Config = Config()
