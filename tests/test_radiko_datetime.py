"""Test for RadikoDateTime."""
from datetime import date, datetime

from freezegun.api import freeze_time
import pytest

from radikopodcast.radiko_datetime import JST, RadikoDate, RadikoDatetime


class TestRadikoDatetime:
    """Test for RadikoDatetime."""

    CASE_TIME_FREE_OLDEST_DAY = [
        (datetime(2021, 1, 7, 21, 55, 15, tzinfo=JST), date(2020, 12, 31)),
        (datetime(2021, 1, 8, 4, 59, 59, tzinfo=JST), date(2020, 12, 31)),
        (datetime(2021, 1, 8, 5, 0, 0, tzinfo=JST), date(2021, 1, 1)),
    ]
    CASE_TIME_FREE_DAY_BEFORE_NEWEST_DAY = [
        (datetime(2021, 1, 7, 21, 55, 15, tzinfo=JST), date(2021, 1, 6)),
        (datetime(2021, 1, 8, 4, 59, 59, tzinfo=JST), date(2021, 1, 6)),
        (datetime(2021, 1, 8, 5, 0, 0, tzinfo=JST), date(2021, 1, 7)),
    ]
    CASE_IS_SAME_RADIKO_DATE = [
        (datetime(2021, 11, 21, 4, 59, 59, tzinfo=JST), datetime(2021, 11, 20, 5, 0, 0, tzinfo=JST), True),
        (datetime(2021, 11, 21, 4, 59, 59, tzinfo=JST), datetime(2021, 11, 21, 5, 0, 0, tzinfo=JST), False),
        (datetime(2021, 11, 20, 5, 0, 0, tzinfo=JST), datetime(2021, 11, 21, 4, 59, 59, tzinfo=JST), True),
        (datetime(2021, 11, 21, 5, 0, 0, tzinfo=JST), datetime(2021, 11, 21, 4, 59, 59, tzinfo=JST), False),
    ]

    @staticmethod
    def test_encode() -> None:
        assert RadikoDatetime.encode(datetime(2023, 3, 12, 17, 59, 25, tzinfo=JST)) == "20230312175925"

    @staticmethod
    def test_decode() -> None:
        assert RadikoDatetime.decode("20230312175925") == datetime(2023, 3, 12, 17, 59, 25, tzinfo=JST)

    @staticmethod
    @freeze_time("2021-11-13 00:00:00", tz_offset=-9)
    def test_download_if_program_has_not_been_downloaded() -> None:
        now = RadikoDatetime.now_jst()
        assert now.strftime("%Y/%m/%d %H:%M:%S %Z") == "2021/11/13 00:00:00 JST"

    @staticmethod
    @pytest.mark.parametrize(
        ("argument", "expect"),
        CASE_TIME_FREE_OLDEST_DAY,
    )
    def test_time_free_oldest_day(argument: datetime, expect: date) -> None:
        assert RadikoDatetime.time_free_oldest_date(argument) == expect

    @staticmethod
    @pytest.mark.parametrize(
        ("argument", "expect"),
        CASE_TIME_FREE_DAY_BEFORE_NEWEST_DAY,
    )
    def test_time_free_day_before_newest_day(argument: datetime, expect: date) -> None:
        assert RadikoDatetime.time_free_day_before_newest_date(argument) == expect

    @staticmethod
    @pytest.mark.parametrize(
        ("datetime_a", "datetime_b", "expect"),
        CASE_IS_SAME_RADIKO_DATE,
    )
    def test_is_same_radiko_date(datetime_a: datetime, datetime_b: datetime, *, expect: bool) -> None:
        assert RadikoDatetime.is_same_radiko_date(datetime_a, datetime_b) == expect


class TestRadikoDate:
    """Test for RadikoDate."""

    @staticmethod
    def test_encode() -> None:
        assert RadikoDate.encode(date(2021, 11, 20)) == "20211120"

    @staticmethod
    def test_decode() -> None:
        assert RadikoDate.decode("20211120") == date(2021, 11, 20)
