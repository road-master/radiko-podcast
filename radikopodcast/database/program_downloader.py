"""Download programs."""
from datetime import date, datetime, timedelta
from logging import getLogger
from typing import Generator

from radikopodcast.database.models import Program
from radikopodcast.radiko_datetime import RadikoDatetime
from radikopodcast.radikoapi.radiko_api import RadikoApi
from radikopodcast.radikoxml.xml_converter import XmlConverterProgram


class ProgramDownloader:
    """Download programs."""

    AREA_ID_DEFAULT = "JP13"  # TOKYO

    def __init__(self, base_datetime: datetime, *, area_id: str = AREA_ID_DEFAULT) -> None:
        self.time_free_oldest_date = RadikoDatetime.time_free_oldest_date(base_datetime)
        self.time_free_day_before_newest_date = RadikoDatetime.time_free_day_before_newest_date(base_datetime)
        self.area_id = area_id
        self.logger = getLogger(__name__)

    def download_all_time_free_programs(self) -> None:
        """Download programs from radiko API."""
        for target_date in self.daterange(self.time_free_oldest_date, self.time_free_day_before_newest_date):
            self.logger.debug("target_date = %04d-%02d-%02d", target_date.year, target_date.month, target_date.day)
            if Program.is_empty(target_date):
                element_tree_radiko = RadikoApi(area_id=self.area_id).get_program(target_date)
                Program.save_all(XmlConverterProgram(target_date, element_tree_radiko, self.area_id).to_model())

    @staticmethod
    def daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
        for day in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(day)
