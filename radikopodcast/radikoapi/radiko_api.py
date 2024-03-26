"""The radiko API."""

from logging import getLogger
from typing import TYPE_CHECKING

from defusedxml import ElementTree

from radikopodcast.radikoapi.requester import Requester

if TYPE_CHECKING:
    from datetime import date

    # Reason: The defusedxml's issue:
    # - defusedxml lacks an Element class · Issue #48 · tiran/defusedxml
    #   https://github.com/tiran/defusedxml/issues/48
    # nosemgrep: python.lang.security.use-defused-xml.use-defused-xml  # noqa: ERA001
    from xml.etree.ElementTree import Element  # nosec B405


class RadikoApi:
    """The radiko API."""

    AREA_ID_DEFAULT = "JP13"  # TOKYO

    def __init__(self, *, area_id: str = AREA_ID_DEFAULT) -> None:
        self.area_id = area_id
        self.logger = getLogger(__name__)

    def get_program(self, target_date: "date") -> "Element":
        return self.get(f"https://radiko.jp/v3/program/date/{target_date.strftime('%Y%m%d')}/{self.area_id}.xml")

    def get_station(self) -> "Element":
        return self.get(f"https://radiko.jp/v3/station/list/{self.area_id}.xml")

    @staticmethod
    def get(url: str) -> "Element":
        # Reason: The defusedxml's responsible.
        return ElementTree.fromstring(Requester.get(url).content, forbid_dtd=True)  # type: ignore[no-any-return]
