"""XML parsers."""
from datetime import date, datetime
from typing import Any, Callable, List
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

# Reason: Following export method in __init__.py from Effective Python 2nd Edition item 85
from errorcollector import MultipleErrorCollector  # type: ignore

from radikopodcast.exceptions import XmlParseError
from radikopodcast.radiko_datetime import RadikoDatetime


class XmlParser:
    """Abstruct XML parser."""

    def __init__(self) -> None:
        self.list_error: List[XmlParseError] = []

    # Reason: Parent method. pylint: disable=no-self-use
    @property
    def validate(self) -> bool:
        """This method validates data."""
        return bool(self.list_error)

    def stock_error(self, method: Callable[[], Any], message: str) -> Any:
        """This method stocks error"""
        with MultipleErrorCollector(XmlParseError, message, self.list_error):
            return method()

    @staticmethod
    def to_string(element: Element) -> str:
        return ElementTree.tostring(element, encoding="unicode")


# Reason: This class converts argument of constructor to property. pylint: disable=too-few-public-methods
class XmlParserProgram(XmlParser):
    """XML parser for program of radiko."""

    def __init__(self, element_tree_program: Element, element_tree_station: Element, target_date: date, area_id: str):
        super().__init__()
        self.element_tree_program = element_tree_program
        self.element_tree_station = element_tree_station
        self.date = target_date
        self.area_id = area_id

    @property
    # Reason: "id" meets requirement of snake_case. pylint: disable=invalid-name
    def id(self) -> str:
        return self.element_tree_program.attrib["id"]

    @property
    # Reason: Can't understand what "ft" points. pylint: disable=invalid-name
    def ft(self) -> datetime:
        return RadikoDatetime.decode(self.element_tree_program.attrib["ft"])

    @property
    # Reason: "to" meets requirement of snake_case. pylint: disable=invalid-name
    def to(self) -> datetime:
        return RadikoDatetime.decode(self.element_tree_program.attrib["to"])

    @property
    def title(self) -> str:
        """Title if find it, otherwise, raises error."""
        element_title = self.element_tree_program.find("title")
        if element_title is None:
            raise XmlParseError(f"Can't find title. XML: {self.to_string(self.element_tree_program)}")
        if element_title.text is None:
            raise XmlParseError(f"No title text. XML: {self.to_string(self.element_tree_program)}")
        return element_title.text

    @property
    def station_id(self) -> str:
        return self.element_tree_station.attrib["id"]

    @property
    def validate(self) -> bool:
        self.stock_error(lambda: self.id, f"Invalid id. XML: {self.to_string(self.element_tree_program)}")
        self.stock_error(lambda: self.ft, f"Invalid ft. XML: {self.to_string(self.element_tree_program)}")
        self.stock_error(lambda: self.to, f"Invalid to. XML: {self.to_string(self.element_tree_program)}")
        self.stock_error(lambda: self.title, f"Invalid title. XML: {self.to_string(self.element_tree_program)}")
        self.stock_error(
            lambda: self.station_id, f"Invalid station id. XML: {self.to_string(self.element_tree_station)}"
        )
        return super().validate


# Reason: This class converts argument of constructor to property. pylint: disable=too-few-public-methods
class XmlParserStation(XmlParser):
    """XML parser for station of radiko."""

    def __init__(self, element_tree_station: Element):
        super().__init__()
        self.element_tree_station = element_tree_station

    @property
    # Reason: "id" meets requirement of snake_case. pylint: disable=invalid-name
    def id(self) -> str:
        """ID if find it, otherwise, raises error."""
        element_id = self.element_tree_station.find("./id")
        if element_id is None:
            raise XmlParseError(f"Can't find id. XML: {self.to_string(self.element_tree_station)}")
        if element_id.text is None:
            raise XmlParseError(f"No id text. XML: {self.to_string(self.element_tree_station)}")
        return element_id.text

    @property
    def name(self) -> str:
        """Name if find it, otherwise, raises error."""
        element_name = self.element_tree_station.find("./name")
        if element_name is None:
            raise XmlParseError(f"Can't find name. XML: {self.to_string(self.element_tree_station)}")
        if element_name.text is None:
            raise XmlParseError(f"No name text. XML: {self.to_string(self.element_tree_station)}")
        return element_name.text

    @property
    def validate(self) -> bool:
        self.stock_error(lambda: self.id, f"Invalid id. XML: {self.to_string(self.element_tree_station)}")
        self.stock_error(lambda: self.name, f"Invalid name. XML: {self.to_string(self.element_tree_station)}")
        return super().validate
