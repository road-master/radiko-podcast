"""Test for Database."""

from datetime import datetime

from freezegun import freeze_time

from radikopodcast.database.program_schedule import ProgramSchedule


class TestDatabase:
    """Test for Database."""

    @staticmethod
    @freeze_time("2021-11-13 05:15:00", tz_offset=-9)
    def test_download_if_program_has_not_been_downloaded() -> None:
        program_schedule = ProgramSchedule()
        program_schedule.download_if_program_has_not_been_downloaded()
        assert program_schedule.last_updated is None

    @staticmethod
    def test_has_downloaded() -> None:
        assert not ProgramSchedule().has_downloaded(datetime(2021, 1, 7, 0, 0, 0))
