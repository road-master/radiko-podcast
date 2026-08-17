# Copyright (C) 2026 Master
"""Test for models.py."""

from datetime import date
from typing import cast

import pytest
from sqlalchemy import and_

from radikopodcast.database.models import ArchiveStatusId
from radikopodcast.database.models import Program
from radikopodcast.database.session_manager import SessionManager

MAX_RETRY_COUNT = 5


class TestProgram:
    """Test for Program."""

    @staticmethod
    @pytest.mark.usefixtures("record_program")
    def test_is_empty() -> None:
        assert Program.is_empty(date(2021, 1, 16)) is False

    @staticmethod
    def test_to_string_none(model_program: Program) -> None:
        model_program.to = None
        with pytest.raises(ValueError, match="None") as excinfo:
            # Reason: Property has logic. pylint: disable=pointless-statement
            model_program.to_string  # noqa: B018
        assert "None" in str(excinfo.value)

    @staticmethod
    def test_ft_string_none(model_program: Program) -> None:
        model_program.ft = None
        with pytest.raises(ValueError, match="None") as excinfo:
            # Reason: Property has logic. pylint: disable=pointless-statement
            model_program.ft_string  # noqa: B018
        assert "None" in str(excinfo.value)

    @pytest.mark.usefixtures("record_program")
    def test_mark_archivable(self) -> None:
        """Method: mark_archivable() should update database record as status: archivable."""
        program = self.find_one("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVABLE
        program.mark_archiving()
        program = self.find_one("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVING
        program.mark_archivable()
        program = self.find_one("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVABLE

    @pytest.mark.usefixtures("record_program")
    def test_mark_retry_or_failed(self) -> None:
        """Method should requeue the program as archivable while retries remain."""
        program = self.find_one("ROPPONGI PASSION PIT")
        assert program.archive_retry_count == 0
        assert program.mark_retry_or_failed(MAX_RETRY_COUNT) == 1
        program = self.find_one("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVABLE.value
        assert program.archive_retry_count == 1
        assert [found.id for found in Program.find(["ROPPONGI PASSION PIT"])] == [program.id]

    @pytest.mark.usefixtures("record_program")
    def test_mark_retry_or_failed_exhausted(self) -> None:
        """Method should mark the program failed once retries are exhausted."""
        program = self.find_one("ROPPONGI PASSION PIT")
        for _ in range(MAX_RETRY_COUNT - 1):
            program.mark_retry_or_failed(MAX_RETRY_COUNT)
        assert program.mark_retry_or_failed(MAX_RETRY_COUNT) == MAX_RETRY_COUNT
        program = self.find_one("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.FAILED.value

    @staticmethod
    def find_one(keyword: str) -> Program:
        with SessionManager() as session:
            list_condition_keyword = [Program.title.like(f"%{keyword}%")]
            return cast(
                "Program",
                session.query(Program).filter(and_(*list_condition_keyword)).order_by(Program.ft.asc()).first(),
            )
