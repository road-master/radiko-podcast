from xml.etree import ElementTree

import pytest

from radikopodcast.exceptions import XmlParseError
from radikopodcast.radikoxml.xml_parser import XmlParserProgram, XmlParserStation


class TestXmlParserStation:
    @staticmethod
    @pytest.mark.parametrize(
        "xml, expect",
        [("<radiko />", "Can't find title. XML: "), ("<radiko><title /></radiko>", "No title text. XML: ")],
    )
    def test_xml_parser_program_title_error(xml: str, expect: str) -> None:
        # To omit coding fixture
        xml_parser_program = XmlParserProgram(ElementTree.fromstring(xml), None, None, "JP13")  # type: ignore
        with pytest.raises(XmlParseError) as excinfo:
            xml_parser_program.title
        assert expect in str(excinfo.value)

    @staticmethod
    @pytest.mark.parametrize(
        "xml, expect", [("<stations />", "Can't find id. XML: "), ("<stations><id /></stations>", "No id text. XML: ")]
    )
    def test_xml_parser_station_id_error(xml: str, expect: str) -> None:
        xml_parser_program = XmlParserStation(ElementTree.fromstring(xml))
        with pytest.raises(XmlParseError) as excinfo:
            xml_parser_program.id
        assert expect in str(excinfo.value)

    @staticmethod
    @pytest.mark.parametrize(
        "xml, expect",
        [("<stations />", "Can't find name. XML: "), ("<stations><name /></stations>", "No name text. XML: ")],
    )
    def test_xml_parser_station_name_error(xml: str, expect: str) -> None:
        xml_parser_program = XmlParserStation(ElementTree.fromstring(xml))
        with pytest.raises(XmlParseError) as excinfo:
            xml_parser_program.name
        assert expect in str(excinfo.value)
