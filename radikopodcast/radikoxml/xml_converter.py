"""XML converter."""

from __future__ import annotations

from abc import abstractmethod
from logging import getLogger
from typing import TYPE_CHECKING
from typing import Generic

from radikopodcast.database.models import Program
from radikopodcast.database.models import Station
from radikopodcast.database.models import TypeVarModelInitByXml as T
from radikopodcast.radikoxml.xml_parser import XmlParser
from radikopodcast.radikoxml.xml_parser import XmlParserProgram
from radikopodcast.radikoxml.xml_parser import XmlParserStation

if TYPE_CHECKING:
    from datetime import date

    # Reason: The defusedxml's issue:
    # - defusedxml lacks an Element class · Issue #48 · tiran/defusedxml
    #   https://github.com/tiran/defusedxml/issues/48
    # nosemgrep: python.lang.security.use-defused-xml.use-defused-xml  # noqa: ERA001
    from xml.etree.ElementTree import Element  # nosec B405


class XmlConverter(Generic[T]):
    """XML converter."""

    def __init__(self) -> None:
        self.logger = getLogger(__name__)

    def to_model(self) -> list[T]:
        """Converts to list of SQLAlchemy model of station of radiko."""
        list_model = list(filter(lambda x: x is not None, self.comprehension_notation()))
        self.logger.debug(list_model)
        # Reason: mypy's bug, see: https://github.com/python/mypy/issues/6847
        return list_model  # type: ignore[return-value]

    @abstractmethod
    def comprehension_notation(self) -> list[T | None]:
        raise NotImplementedError  # pragma: no cover

    def create_model(self, xml_parser: XmlParser, model_class: type[T]) -> T | None:
        if xml_parser.validate:
            self.logger.error(xml_parser.list_error)
            return None
        return model_class(xml_parser)


class XmlConverterProgram(XmlConverter[Program]):
    """XML converter for program of radiko."""

    def __init__(self, target_date: date, element_tree_radiko: Element, area_id: str) -> None:
        super().__init__()
        self.target_date = target_date
        self.element_tree_radiko = element_tree_radiko
        self.area_id = area_id

    def comprehension_notation(self) -> list[Program | None]:
        return [
            self.create_model(self.create_xml_parser(element_tree_program, element_tree_station), Program)
            for element_tree_station in self.element_tree_radiko.findall("./stations/station")
            for element_tree_program in element_tree_station.findall("./progs/prog")
        ]

    def create_xml_parser(self, element_tree_program: Element, element_tree_station: Element) -> XmlParserProgram:
        return XmlParserProgram(element_tree_program, element_tree_station, self.target_date, self.area_id)


class XmlConverterStation(XmlConverter[Station]):
    """XML converter for station of radiko."""

    def __init__(self, element_tree_list_station: Element) -> None:
        super().__init__()
        self.element_tree_list_station = element_tree_list_station

    def comprehension_notation(self) -> list[Station | None]:
        return [
            self.create_model(XmlParserStation(element_tree_station), Station)
            for element_tree_station in self.element_tree_list_station.findall("./station")
        ]
