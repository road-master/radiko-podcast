"""This module implements SQLAlchemy database models."""
from __future__ import annotations

import datetime
from abc import abstractmethod

# Reason: For type hint. pylint: disable=unused-import
from enum import IntEnum
from typing import Generic, Iterable, List, TypeVar, cast

from inflector import Inflector
from sqlalchemy import DATETIME, Column, String, and_, func, or_
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm.interfaces import MapperProperty
from sqlalchemy.sql.schema import ForeignKey, MetaData
from sqlalchemy.sql.sqltypes import DATE, INTEGER

from radikopodcast.database.session_manager import SessionManager
from radikopodcast.radiko_datetime import RadikoDatetime
from radikopodcast.radikoxml.xml_parser import XmlParser, XmlParserProgram, XmlParserStation


class ArchiveStatusId(IntEnum):
    """This class implements file for CSV convert id on database."""

    ARCHIVABLE = 0
    ARCHIVING = 1
    SUSPENDED = 2
    FAILED = 3
    ARCHIVED = 4


Base = declarative_base(metadata=MetaData())

TypeVarXmlParser = TypeVar("TypeVarXmlParser", bound=XmlParser)


class ModelInitByXml(Base, Generic[TypeVarXmlParser]):
    """Abstract class of Model which initialized by XML."""

    __abstract__ = True

    @declared_attr
    # Reason: @declared_attr marks method as class level.
    # see: https://docs.sqlalchemy.org/en/14/orm/mapping_api.html#class-mapping-api
    # pylint: disable=no-self-argument
    def __tablename__(cls) -> MapperProperty[str]:
        # Reason: "cls" is not instance.
        # pylint: disable=no-member
        return Inflector().pluralize(cls.__name__.lower())

    def __init__(self, xml_parser: TypeVarXmlParser):
        super().__init__()
        self.init(xml_parser)

    @abstractmethod
    def init(self, xml_parser: TypeVarXmlParser) -> None:
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def save_all(cls, models: "Iterable[TypeVarModelInitByXml]") -> None:
        """This method insert Store models into database."""
        with SessionManager() as session:
            with session.begin():
                session.add_all(models)


# Reason: Mypy won't support TypeVar bounding generic type.
# see:
#  - `TypeVar`s cannot refer to type variables · Issue #2756 · python/mypy
#    https://github.com/python/mypy/issues/2756#issuecomment-579496164
TypeVarModelInitByXml = TypeVar("TypeVarModelInitByXml", bound=ModelInitByXml)  # type: ignore


class Station(ModelInitByXml[XmlParserStation]):
    """Station of radiko."""

    id = Column(String(255), primary_key=True)
    name = Column(String(255))
    list_program: Mapped[List[Program]] = relationship("Program", backref="station")
    transfer_target = Column(String(255))

    def init(self, xml_parser: XmlParserStation) -> None:
        # Reason: "id" meets requirement of snake_case. pylint: disable=invalid-name
        self.id = xml_parser.id
        self.name = xml_parser.name

    @staticmethod
    def is_empty() -> bool:
        with SessionManager() as session:
            count = cast(tuple[int], session.query(func.count(Station.id)).one())
            return count == (0,)


class Program(ModelInitByXml[XmlParserProgram]):
    """Program of radiko."""

    # Reason: Model. pylint: disable=too-many-instance-attributes
    id = Column(String(255), primary_key=True)
    to = Column(DATETIME)
    ft = Column(DATETIME)
    title = Column(String(255))
    station_id: str = Column(String, ForeignKey("stations.id"), nullable=False)
    date = Column(DATE)
    area_id = Column(String(255))
    archive_status = Column(INTEGER)

    def init(self, xml_parser: XmlParserProgram) -> None:
        # Reason: "id" meets requirement of snake_case. pylint: disable=invalid-name
        self.id = xml_parser.id
        # Reason: Can't understand what "ft" points. pylint: disable=invalid-name
        self.ft = xml_parser.ft
        # Reason: "to" meets requirement of snake_case. pylint: disable=invalid-name
        self.to = xml_parser.to
        self.title = xml_parser.title
        self.station_id = xml_parser.station_id
        self.date = xml_parser.date
        self.area_id = xml_parser.area_id
        self.archive_status = ArchiveStatusId.ARCHIVABLE.value

    def mark_archivable(self) -> None:
        Program.mark(self, ArchiveStatusId.ARCHIVABLE)

    def mark_archiving(self) -> None:
        Program.mark(self, ArchiveStatusId.ARCHIVING)

    def mark_suspended(self) -> None:
        Program.mark(self, ArchiveStatusId.SUSPENDED)

    def mark_failed(self) -> None:
        Program.mark(self, ArchiveStatusId.FAILED)

    def mark_archived(self) -> None:
        Program.mark(self, ArchiveStatusId.ARCHIVED)

    @staticmethod
    def mark(program: Program, archive_id: ArchiveStatusId) -> None:
        with SessionManager() as session:
            selected_program = session.query(Program).with_for_update().filter_by(id=program.id).one()
            selected_program.archive_status = archive_id.value
            session.flush()

    @property
    def ft_string(self) -> str:
        assert self.ft is not None
        return RadikoDatetime.encode(self.ft)

    @property
    def to_string(self) -> str:
        assert self.to is not None
        return RadikoDatetime.encode(self.to)

    @staticmethod
    def is_empty(target_date: datetime.date) -> bool:
        with SessionManager() as session:
            count = cast(tuple[int], session.query(func.count(Program.id)).filter(Program.date == target_date).one())
            return count == (0,)

    @staticmethod
    def find(keywords: List[str]) -> List[Program]:
        """This method select Store model from database."""
        with SessionManager() as session:
            list_condition_keyword = [Program.title.like(f"%{keyword}%") for keyword in keywords]
            return (
                session.query(Program)
                .filter(
                    and_(or_(*list_condition_keyword), Program.archive_status.is_(ArchiveStatusId.ARCHIVABLE.value))
                )
                .order_by(Program.ft.asc())
                .all()
            )

    @staticmethod
    def delete(boundary_date: datetime.date) -> None:
        with SessionManager() as session:
            session.query(Program).filter(Program.date < boundary_date).delete()
