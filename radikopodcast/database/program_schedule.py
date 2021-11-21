"""Program schedule."""
from datetime import datetime
from typing import List, Optional

from radikopodcast.database.database import Database
from radikopodcast.database.models import Program, Station
from radikopodcast.database.program_downloader import ProgramDownloader
from radikopodcast.radiko_datetime import RadikoDatetime
from radikopodcast.radikoapi.radiko_api import RadikoApi
from radikopodcast.radikoxml.xml_converter import XmlConverterStation


class ProgramSchedule:
    """Program schedule."""

    AREA_ID_DEFAULT = "JP13"  # TOKYO

    def __init__(self, *, area_id: str = AREA_ID_DEFAULT) -> None:
        # pylint bug, see: https://github.com/PyCQA/pylint/issues/3882
        # pylint: disable=unsubscriptable-object
        self.last_updated: Optional[datetime] = None
        self.area_id = area_id
        self.database = Database()
        if Station.is_empty():
            Station.save_all(XmlConverterStation(RadikoApi(area_id=self.area_id).get_station()).to_model())

    @staticmethod
    def search(keywords: List[str]) -> List[Program]:
        return Program.find(keywords)

    def download_if_program_has_not_been_downloaded(self) -> None:
        now = RadikoDatetime.now_jst()
        if self.has_downloaded(now):
            return
        self.add(now)
        self.remove(now)
        self.last_updated = now

    def has_downloaded(self, now: datetime) -> bool:
        return (
            self.last_updated is not None
            and RadikoDatetime.is_same_radiko_date(now, self.last_updated)
            or now.hour == 5
            and now.minute <= 15
        )

    def add(self, now: datetime) -> None:
        """Adds programs from radiko API."""
        program_downloader = ProgramDownloader(now, area_id=self.area_id)
        program_downloader.download_all_time_free_programs()

    @staticmethod
    def remove(now: datetime) -> None:
        Program.delete(RadikoDatetime.time_free_oldest_date(now))
