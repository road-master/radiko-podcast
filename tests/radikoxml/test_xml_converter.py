"""Tests for xmp_converter.py."""
from datetime import date, datetime
from typing import TYPE_CHECKING

from defusedxml import ElementTree

from radikopodcast.radiko_datetime import JST
from radikopodcast.radikoxml.xml_converter import XmlConverterProgram, XmlConverterStation

if TYPE_CHECKING:
    # Reason: The defusedxml's issue:
    # - defusedxml lacks an Element class · Issue #48 · tiran/defusedxml
    #   https://github.com/tiran/defusedxml/issues/48
    from xml.etree.ElementTree import Element  # nosec B405

    from radikopodcast.database.models import Program, Station


class TestXmlConverter:
    """Tests for XmlConverter."""

    def test_to_model_program(self, element_tree_program: "Element") -> None:
        """XmlConverterProgram should convert element tree to list of Model."""
        expect_list_program = 99
        list_program = XmlConverterProgram(date(2021, 1, 16), element_tree_program, "JP13").to_model()
        assert len(list_program) == expect_list_program
        program = list_program[0]
        assert program is not None
        self.check_program1(program)
        self.check_program2(program)

    @staticmethod
    def check_program1(program: "Program") -> None:
        assert program.id == "9552146705"
        assert program.ft == datetime(2021, 1, 16, 5, 0, tzinfo=JST)
        assert program.to == datetime(2021, 1, 16, 6, 0, tzinfo=JST)

    @staticmethod
    def check_program2(program: "Program") -> None:
        assert program.title == "ZAPPA"
        assert program.station_id == "FMJ"
        assert program.date == date(2021, 1, 16)
        assert program.archive_status == 0

    def test_to_model_station(self, element_tree_station: "Element") -> None:
        expect_len_list_station = 15
        list_station = XmlConverterStation(element_tree_station).to_model()
        assert len(list_station) == expect_len_list_station
        station = list_station[0]
        assert station is not None
        self.check_station(station)

    @staticmethod
    def check_station(station: "Station") -> None:
        assert station.id == "TBS"
        assert station.name == "TBSラジオ"
        assert station.list_program == []
        assert station.transfer_target is None

    @staticmethod
    def test_to_model_validate_error(xml_station_name_lacked: str) -> None:
        # Reason: To check value details. pylint: disable=use-implicit-booleaness-not-comparison
        assert XmlConverterStation(ElementTree.fromstring(xml_station_name_lacked, forbid_dtd=True)).to_model() == []
