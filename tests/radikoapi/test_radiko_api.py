"""Tests for radiko_api.py."""

from datetime import date
from typing import TYPE_CHECKING

from defusedxml import ElementTree
import pytest

from radikopodcast.radikoapi.radiko_api import RadikoApi

if TYPE_CHECKING:
    # Reason: The defusedxml's issue:
    # - defusedxml lacks an Element class · Issue #48 · tiran/defusedxml
    #   https://github.com/tiran/defusedxml/issues/48
    from xml.etree.ElementTree import Element  # nosec B405


class TestRadikoApi:
    """Tests for RadikoApi."""

    @pytest.mark.usefixtures("_mock_requests_program")
    def test_get_program(self, xml_program: str) -> None:
        element_tree_program = RadikoApi().get_program(date(2021, 1, 16))
        assert self.to_string(element_tree_program) == xml_program

    @pytest.mark.usefixtures("_mock_requests_station")
    def test_get_station(self, xml_station: str) -> None:
        element_tree_station = RadikoApi().get_station()
        assert self.to_string(element_tree_station) == xml_station

    @staticmethod
    def to_string(element_tree: "Element") -> str:
        # Reason: The defusedxml's responsible.
        return ElementTree.tostring(element_tree, encoding="unicode")  # type: ignore[no-any-return]
