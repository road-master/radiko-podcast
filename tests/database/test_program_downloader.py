"""Tests for program_downloader.py."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from freezegun import freeze_time
from pytest_mock import MockerFixture
from radikoplaylist.exceptions import HttpRequestTimeoutError

from radikopodcast.database.models import Program
from radikopodcast.database.program_downloader import ProgramDownloader
from radikopodcast.radiko_datetime import JST
from radikopodcast.radikoapi.radiko_api import RadikoApi


class TestProgramDownloader:
    """Tests for ProgramDownloader."""

    @staticmethod
    @pytest.mark.usefixtures("database_session_with_schema", "_mock_requests_station")
    @freeze_time("2021-01-17 20:00:00", tz_offset=+9)
    def test_download_all_time_free_programs_continues_after_api_timeout(mocker: MockerFixture) -> None:
        """A timeout on one date must not abort other dates or raise to caller."""
        now = datetime(2021, 1, 17, 20, 0, 0, tzinfo=JST)
        downloader = ProgramDownloader(now)

        fake_xml = MagicMock()
        timeout_day = 14
        number_of_dates_in_range = 7  # Jan 10-16
        expected_save_count = number_of_dates_in_range - 1  # one date times out

        def get_program_side_effect(target_date: datetime) -> str:
            if target_date.day == timeout_day:
                msg = "simulated timeout"
                raise HttpRequestTimeoutError(msg)
            return fake_xml

        mocker.patch.object(RadikoApi, "get_program", side_effect=get_program_side_effect)
        mocker.patch.object(Program, "is_empty", return_value=True)
        mock_save_all = mocker.patch.object(Program, "save_all")
        mocker.patch("radikopodcast.database.program_downloader.XmlConverterProgram")

        # Must not raise despite the timeout on Jan 14
        downloader.download_all_time_free_programs()

        assert mock_save_all.call_count == expected_save_count
