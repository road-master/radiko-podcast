"""XML parsers."""

from typing import Any, Callable, TYPE_CHECKING

from defusedxml import ElementTree
from errorcollector import MultipleErrorCollector

from radikopodcast.exceptions import XmlParseError
from radikopodcast.radiko_datetime import RadikoDatetime

if TYPE_CHECKING:
    from datetime import date, datetime

    # Reason: The defusedxml's issue:
    # - defusedxml lacks an Element class · Issue #48 · tiran/defusedxml
    #   https://github.com/tiran/defusedxml/issues/48
    # nosemgrep: python.lang.security.use-defused-xml.use-defused-xml  # noqa: ERA001
    from xml.etree.ElementTree import Element  # nosec B405


class XmlParser:
    """Abstract XML parser."""

    def __init__(self) -> None:
        self.list_error: list[XmlParseError] = []

    @property
    def validate(self) -> bool:
        """This method validates data."""
        return bool(self.list_error)

    def stock_error(self, method: Callable[[], Any], message: str) -> Any:
        """This method stocks error."""
        with MultipleErrorCollector(XmlParseError, message, self.list_error):
            return method()

    @staticmethod
    def to_string(element: "Element") -> str:
        # Reason: The defusedxml's responsible.
        return ElementTree.tostring(element, encoding="unicode")  # type: ignore[no-any-return]


# Reason: This class converts argument of constructor to property. pylint: disable=too-few-public-methods
class XmlParserProgram(XmlParser):
    """XML parser for program of radiko."""

    def __init__(
        self,
        element_tree_program: "Element",
        element_tree_station: "Element",
        target_date: "date",
        area_id: str,
    ) -> None:
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
    def ft(self) -> "datetime":
        return RadikoDatetime.decode(self.element_tree_program.attrib["ft"])

    @property
    # Reason: "to" meets requirement of snake_case. pylint: disable=invalid-name
    def to(self) -> "datetime":
        return RadikoDatetime.decode(self.element_tree_program.attrib["to"])

    @property
    def title(self) -> str:
        """Title if find it, otherwise, raises error."""
        element_title = self.element_tree_program.find("title")
        if element_title is None:
            message = f"Can't find title. XML: {self.to_string(self.element_tree_program)}"
            raise XmlParseError(message)
        if element_title.text is None:
            message = f"No title text. XML: {self.to_string(self.element_tree_program)}"
            raise XmlParseError(message)
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
            lambda: self.station_id,
            f"Invalid station id. XML: {self.to_string(self.element_tree_station)}",
        )
        return super().validate


# Reason: This class converts argument of constructor to property. pylint: disable=too-few-public-methods
class XmlParserStation(XmlParser):
    """XML parser for station of radiko."""

    def __init__(self, element_tree_station: "Element") -> None:
        super().__init__()
        self.element_tree_station = element_tree_station

    @property
    # Reason: "id" meets requirement of snake_case. pylint: disable=invalid-name
    def id(self) -> str:
        """ID if find it, otherwise, raises error."""
        element_id = self.element_tree_station.find("./id")
        if element_id is None:
            message = f"Can't find id. XML: {self.to_string(self.element_tree_station)}"
            raise XmlParseError(message)
        if element_id.text is None:
            message = f"No id text. XML: {self.to_string(self.element_tree_station)}"
            raise XmlParseError(message)
        return element_id.text

    @property
    def name(self) -> str:
        """Name if find it, otherwise, raises error."""
        element_name = self.element_tree_station.find("./name")
        if element_name is None:
            message = f"Can't find name. XML: {self.to_string(self.element_tree_station)}"
            raise XmlParseError(message)
        if element_name.text is None:
            message = f"No name text. XML: {self.to_string(self.element_tree_station)}"
            raise XmlParseError(message)
        return element_name.text

    @property
    def validate(self) -> bool:
        self.stock_error(lambda: self.id, f"Invalid id. XML: {self.to_string(self.element_tree_station)}")
        self.stock_error(lambda: self.name, f"Invalid name. XML: {self.to_string(self.element_tree_station)}")
        return super().validate
