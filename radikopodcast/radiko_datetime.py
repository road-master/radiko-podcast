"""Datetime for radiko specification."""
from datetime import date, datetime, timedelta, timezone


class RadikoDatetime:
    """Datetime for radiko specification."""

    FORMAT_CODE = "%Y%m%d%H%M%S"

    @staticmethod
    def encode(argument_datetime: datetime) -> str:
        return argument_datetime.strftime(RadikoDatetime.FORMAT_CODE)

    @staticmethod
    def decode(argument_string: str) -> datetime:
        return datetime.strptime(argument_string, RadikoDatetime.FORMAT_CODE)

    @staticmethod
    def time_free_oldest_date(now: datetime) -> date:
        return (now - timedelta(days=7, hours=5)).date()

    @staticmethod
    def time_free_day_before_newest_date(now: datetime) -> date:
        return (now - timedelta(days=1, hours=5)).date()

    @staticmethod
    def now_jst() -> datetime:
        return datetime.now(tz=timezone(timedelta(hours=+9), "JST"))

    @staticmethod
    def is_same_radiko_date(datetime_a: datetime, datetime_b: datetime) -> bool:
        return (datetime_a - timedelta(hours=5)).date() == (datetime_b - timedelta(hours=5)).date()


class RadikoDate:
    """Date for radiko specification."""

    FORMAT_CODE = "%Y%m%d"

    @staticmethod
    def encode(argument_datetime: date) -> str:
        return argument_datetime.strftime(RadikoDate.FORMAT_CODE)

    @staticmethod
    def decode(argument_string: str) -> date:
        return datetime.strptime(argument_string, RadikoDate.FORMAT_CODE).date()
