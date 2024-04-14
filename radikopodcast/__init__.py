"""Top-level package for radiko Podcast."""

__author__ = """Master"""
__email__ = "roadmasternavi@gmail.com"
__version__ = "1.0.3"

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from radikopodcast.config import Config

Session = scoped_session(sessionmaker(bind=create_engine("sqlite://")))
CONFIG: Config = Config()
