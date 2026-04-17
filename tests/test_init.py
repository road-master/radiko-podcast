"""Tests for radikopodcast/__init__.py."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine

from radikopodcast.database.models import Base


def test_programs_db_is_created(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """programs.db is created in the current directory when the engine is initialized."""
    monkeypatch.chdir(tmp_path)
    engine = create_engine("sqlite:///programs.db")
    Base.metadata.create_all(engine)
    assert (tmp_path / "programs.db").exists()
