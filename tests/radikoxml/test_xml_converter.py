from datetime import date, datetime
from xml.etree import ElementTree

from radikopodcast.database.models import Program, Station
from radikopodcast.radikoxml.xml_converter import XmlConverterProgram, XmlConverterStation


class TestXmlConverter:
    def test_to_model_program(self, element_tree_program: ElementTree.Element) -> None:
        list_program = XmlConverterProgram(date(2021, 1, 16), element_tree_program, "JP13").to_model()
        assert len(list_program) == 99
        program = list_program[0]
        assert program is not None
        self.check_program1(program)
        self.check_program2(program)

    @staticmethod
    def check_program1(program: Program) -> None:
        assert program.id == "9552146705"
        assert program.ft == datetime(2021, 1, 16, 5, 0)
        assert program.to == datetime(2021, 1, 16, 6, 0)

    @staticmethod
    def check_program2(program: Program) -> None:
        assert program.title == "ZAPPA"
        assert program.station_id == "FMJ"
        assert program.date == date(2021, 1, 16)
        assert program.archive_status == 0

    def test_to_model_station(self, element_tree_station: ElementTree.Element) -> None:
        list_station = XmlConverterStation(element_tree_station).to_model()
        assert len(list_station) == 15
        station = list_station[0]
        assert station is not None
        self.check_station(station)

    @staticmethod
    def check_station(station: Station) -> None:
        assert station.id == "TBS"
        assert station.name == "TBSラジオ"
        assert station.list_program == []
        assert station.transfer_target is None

    @staticmethod
    def test_to_model_validate_error(xml_station_name_lacked: str) -> None:
        assert XmlConverterStation(ElementTree.fromstring(xml_station_name_lacked)).to_model() == []
