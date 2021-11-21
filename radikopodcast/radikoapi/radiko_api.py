"""radiko API."""
from datetime import date
from logging import getLogger
from xml.etree import ElementTree

from radikopodcast.radikoapi.requester import Requester


class RadikoApi:
    """radiko API."""

    AREA_ID_DEFAULT = "JP13"  # TOKYO

    def __init__(self, *, area_id: str = AREA_ID_DEFAULT) -> None:
        self.area_id = area_id
        self.logger = getLogger(__name__)

    def get_program(self, target_date: date) -> ElementTree.Element:
        return self.get(f"http://radiko.jp/v3/program/date/{target_date.strftime('%Y%m%d')}/{self.area_id}.xml")

    def get_station(self) -> ElementTree.Element:
        return self.get(f"http://radiko.jp/v3/station/list/{self.area_id}.xml")

    @staticmethod
    def get(url: str) -> ElementTree.Element:
        return ElementTree.fromstring(Requester.get(url).content)
