"""Program schedule."""

from __future__ import annotations

from typing import TYPE_CHECKING

from radikopodcast.database.database import Database
from radikopodcast.database.models import Program
from radikopodcast.database.models import Station
from radikopodcast.database.program_downloader import ProgramDownloader
from radikopodcast.radiko_datetime import RadikoDatetime
from radikopodcast.radikoapi.radiko_api import RadikoApi
from radikopodcast.radikoxml.xml_converter import XmlConverterStation

if TYPE_CHECKING:
    from datetime import datetime


class ProgramSchedule:
    """Program schedule."""

    AREA_ID_DEFAULT = "JP13"  # TOKYO
    HOUR_WHEN_RADIKO_PROGRAM_UPDATE = 5
    MINUTE_MARGIN_WHEN_RADIKO_PROGRAM_UPDATE = 15

    def __init__(self, *, area_id: str = AREA_ID_DEFAULT, radiko_session: str | None = None) -> None:
        # pylint bug, see: https://github.com/PyCQA/pylint/issues/3882
        # pylint: disable=unsubscriptable-object
        self.last_updated: datetime | None = None
        self.area_id = area_id
        self.radiko_session = radiko_session
        self.database = Database()
        if Station.is_empty():
            Station.save_all(XmlConverterStation(RadikoApi(area_id=self.area_id).get_station()).to_model())

    @staticmethod
    def search(keywords: list[str]) -> list[Program]:
        return Program.find(keywords)

    def download_if_program_has_not_been_downloaded(self) -> None:
        now = RadikoDatetime.now_jst()
        if self.has_downloaded(now):
            return
        self.add(now)
        self.remove(now)
        self.last_updated = now

    def has_downloaded(self, now: datetime) -> bool:
        return (self.last_updated is not None and RadikoDatetime.is_same_radiko_date(now, self.last_updated)) or (
            now.hour == self.HOUR_WHEN_RADIKO_PROGRAM_UPDATE
            and now.minute <= self.MINUTE_MARGIN_WHEN_RADIKO_PROGRAM_UPDATE
        )

    def add(self, now: datetime) -> None:
        """Adds programs from radiko API."""
        program_downloader = ProgramDownloader(now, area_id=self.area_id, radiko_session=self.radiko_session)
        program_downloader.download_all_time_free_programs()

    def remove(self, now: datetime) -> None:
        oldest = (
            RadikoDatetime.timefree30_oldest_date(now)
            if self.radiko_session
            else RadikoDatetime.time_free_oldest_date(now)
        )
        Program.delete(oldest)
