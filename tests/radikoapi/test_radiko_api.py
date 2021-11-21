from datetime import date
from xml.etree import ElementTree

import pytest

from radikopodcast.radikoapi.radiko_api import RadikoApi


class TestRadikoApi:
    @pytest.mark.usefixtures("mock_requests_program")
    def test_get_program(self, xml_program: str) -> None:
        element_tree_program = RadikoApi().get_program(date(2021, 1, 16))
        assert self.to_string(element_tree_program) == xml_program

    @pytest.mark.usefixtures("mock_requests_station")
    def test_get_station(self, xml_station: str) -> None:
        element_tree_station = RadikoApi().get_station()
        assert self.to_string(element_tree_station) == xml_station

    @staticmethod
    def to_string(element_tree: ElementTree.Element) -> str:
        return ElementTree.tostring(element_tree, encoding="unicode")
