# Copyright (C) 2026 Master
"""Test for models.py."""

from collections.abc import Callable
from datetime import date

import pytest

from radikopodcast.database.models import ArchiveStatusId
from radikopodcast.database.models import Program

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

    @staticmethod
    @pytest.mark.usefixtures("record_program")
    def test_mark_archivable(find_program_by_keyword: Callable[[str], Program]) -> None:
        """Method: mark_archivable() should update database record as status: archivable."""
        program = find_program_by_keyword("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVABLE
        program.mark_archiving()
        program = find_program_by_keyword("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVING
        program.mark_archivable()
        program = find_program_by_keyword("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVABLE

    @staticmethod
    @pytest.mark.usefixtures("record_program")
    def test_mark_retry_or_failed(find_program_by_keyword: Callable[[str], Program]) -> None:
        """Method should requeue the program as archivable while retries remain."""
        program = find_program_by_keyword("ROPPONGI PASSION PIT")
        assert program.archive_retry_count == 0
        assert program.mark_retry_or_failed(MAX_RETRY_COUNT) == 1
        program = find_program_by_keyword("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.ARCHIVABLE.value
        assert program.archive_retry_count == 1
        assert [found.id for found in Program.find(["ROPPONGI PASSION PIT"])] == [program.id]

    @staticmethod
    @pytest.mark.usefixtures("record_program")
    def test_mark_retry_or_failed_exhausted(find_program_by_keyword: Callable[[str], Program]) -> None:
        """Method should mark the program failed once retries are exhausted."""
        program = find_program_by_keyword("ROPPONGI PASSION PIT")
        for _ in range(MAX_RETRY_COUNT - 1):
            program.mark_retry_or_failed(MAX_RETRY_COUNT)
        assert program.mark_retry_or_failed(MAX_RETRY_COUNT) == MAX_RETRY_COUNT
        program = find_program_by_keyword("ROPPONGI PASSION PIT")
        assert program.archive_status == ArchiveStatusId.FAILED.value
