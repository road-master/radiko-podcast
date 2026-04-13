"""Datetime for radiko specification."""

from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone

JST = timezone(timedelta(hours=+9), "JST")
HOUR_BORDER_OF_RADIKO_DATE = 5


class RadikoDatetime:
    """Datetime for radiko specification."""

    FORMAT_CODE = "%Y%m%d%H%M%S"

    @staticmethod
    def encode(argument_datetime: datetime) -> str:
        return argument_datetime.strftime(RadikoDatetime.FORMAT_CODE)

    @staticmethod
    def decode(argument_string: str) -> datetime:
        return datetime.strptime(argument_string, RadikoDatetime.FORMAT_CODE).replace(tzinfo=JST)

    @staticmethod
    def time_free_oldest_date(now: datetime) -> date:
        return (now - timedelta(days=7, hours=5)).date()

    @staticmethod
    def timefree30_oldest_date(now: datetime) -> date:
        return (now - timedelta(days=30, hours=5)).date()

    @staticmethod
    def time_free_day_before_newest_date(now: datetime) -> date:
        return (now - timedelta(days=1, hours=5)).date()

    @staticmethod
    def now_jst() -> datetime:
        return datetime.now(tz=JST)

    @staticmethod
    def is_same_radiko_date(datetime_a: datetime, datetime_b: datetime) -> bool:
        return (datetime_a - timedelta(hours=5)).date() == (datetime_b - timedelta(hours=5)).date()

    @staticmethod
    def is_timefree30_required(program_ft: datetime) -> bool:
        """Returns whether the program is available without time-free 30-day download."""
        time_free_oldest_date = RadikoDatetime.time_free_oldest_date(RadikoDatetime.now_jst())
        radiko_date_of_program_ft = RadikoDate.radiko_date(program_ft)
        return radiko_date_of_program_ft < time_free_oldest_date


class RadikoDate:
    """Date for radiko specification."""

    FORMAT_CODE = "%Y%m%d"

    @staticmethod
    def encode(argument_datetime: date) -> str:
        return argument_datetime.strftime(RadikoDate.FORMAT_CODE)

    @staticmethod
    def decode(argument_string: str) -> date:
        return datetime.strptime(argument_string, RadikoDate.FORMAT_CODE).replace(tzinfo=JST).date()

    @staticmethod
    def radiko_date(date_time: datetime) -> date:
        """Returns the date of the program ft belongs to."""
        if date_time.hour < HOUR_BORDER_OF_RADIKO_DATE:
            return (date_time - timedelta(days=1)).date()
        return date_time.date()
