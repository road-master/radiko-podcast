"""Tests for xml_parser.py."""

from defusedxml import ElementTree
import pytest

from radikopodcast.exceptions import XmlParseError
from radikopodcast.radikoxml.xml_parser import XmlParserProgram, XmlParserStation


class TestXmlParserStation:
    """Tests for XmlParserStation."""

    @staticmethod
    @pytest.mark.parametrize(
        ("xml", "expect"),
        [("<radiko />", "Can't find title. XML: "), ("<radiko><title /></radiko>", "No title text. XML: ")],
    )
    def test_xml_parser_program_title_error(xml: str, expect: str) -> None:
        """XmlParserProgram should raise XmpParserError when XML is invalid."""
        # Reason: To omit coding fixture
        element_tree = ElementTree.fromstring(xml, forbid_dtd=True)
        parser = XmlParserProgram(element_tree, None, None, "JP13")  # type: ignore[arg-type]
        with pytest.raises(XmlParseError) as excinfo:
            # Reason: Property has logic. pylint: disable=pointless-statement
            parser.title  # noqa: B018
        assert expect in str(excinfo.value)

    @staticmethod
    @pytest.mark.parametrize(
        ("xml", "expect"),
        [("<stations />", "Can't find id. XML: "), ("<stations><id /></stations>", "No id text. XML: ")],
    )
    def test_xml_parser_station_id_error(xml: str, expect: str) -> None:
        """XmlParserProgram should raise XmpParserError when XML is invalid."""
        xml_parser_program = XmlParserStation(ElementTree.fromstring(xml, forbid_dtd=True))
        with pytest.raises(XmlParseError) as excinfo:
            # Reason: Property has logic. pylint: disable=pointless-statement
            xml_parser_program.id  # noqa: B018
        assert expect in str(excinfo.value)

    @staticmethod
    @pytest.mark.parametrize(
        ("xml", "expect"),
        [("<stations />", "Can't find name. XML: "), ("<stations><name /></stations>", "No name text. XML: ")],
    )
    def test_xml_parser_station_name_error(xml: str, expect: str) -> None:
        """XmlParserProgram should raise XmpParserError when XML is invalid."""
        xml_parser_program = XmlParserStation(ElementTree.fromstring(xml, forbid_dtd=True))
        with pytest.raises(XmlParseError) as excinfo:
            # Reason: Property has logic. pylint: disable=pointless-statement
            xml_parser_program.name  # noqa: B018
        assert expect in str(excinfo.value)
