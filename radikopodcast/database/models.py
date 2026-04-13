"""This module implements SQLAlchemy database models."""

from __future__ import annotations

# Reason: To prevent following error:
#   E   sqlalchemy.orm.exc.MappedAnnotationError: Could not resolve all types within mapped annotation: "Mapped[datetime.datetime | None]".  Ensure all types are written correctly and are imported within the module in use.
import datetime  # noqa: TC003
from abc import abstractmethod
from enum import IntEnum
from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar
from typing import cast

from inflector import Inflector
from sqlalchemy import DATETIME
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import or_
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.schema import MetaData
from sqlalchemy.sql.sqltypes import DATE
from sqlalchemy.sql.sqltypes import INTEGER

from radikopodcast.database.session_manager import SessionManager
from radikopodcast.radiko_datetime import RadikoDatetime
from radikopodcast.radikoxml.xml_parser import XmlParser
from radikopodcast.radikoxml.xml_parser import XmlParserProgram
from radikopodcast.radikoxml.xml_parser import XmlParserStation

if TYPE_CHECKING:
    from collections.abc import Iterable


class ArchiveStatusId(IntEnum):
    """This class implements file for CSV convert id on database."""

    ARCHIVABLE = 0
    ARCHIVING = 1
    SUSPENDED = 2
    FAILED = 3
    ARCHIVED = 4


# Reason: To follow SQLAlchemy 2.0 style of declarative mapping:
# - Declarative Mapping Styles — SQLAlchemy 2.0 Documentation
#   https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html
class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Declarative base class."""

    metadata = MetaData()


TypeVarXmlParser = TypeVar("TypeVarXmlParser", bound=XmlParser)


class ModelInitByXml(Base, Generic[TypeVarXmlParser]):
    """Abstract class of Model which initialized by XML."""

    __abstract__ = True

    @declared_attr.directive
    # Reason: @declared_attr marks method as class level.
    # see: https://docs.sqlalchemy.org/en/20/orm/declarative_mixins.html
    # pylint: disable=no-self-argument
    def __tablename__(cls) -> str:  # noqa: N805
        return str(Inflector().pluralize(cls.__name__.lower()))

    def __init__(self, xml_parser: TypeVarXmlParser) -> None:
        super().__init__()
        self.init(xml_parser)

    @abstractmethod
    def init(self, xml_parser: TypeVarXmlParser) -> None:
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def save_all(cls, models: Iterable[TypeVarModelInitByXml]) -> None:
        """This method insert Store models into database."""
        with SessionManager() as session, session.begin():
            session.add_all(models)


# Reason: Mypy won't support TypeVar bounding generic type.
# see:
#  - `TypeVar`s cannot refer to type variables · Issue #2756 · python/mypy
#    https://github.com/python/mypy/issues/2756#issuecomment-579496164
TypeVarModelInitByXml = TypeVar("TypeVarModelInitByXml", bound=ModelInitByXml)  # type: ignore[type-arg]


class Station(ModelInitByXml[XmlParserStation]):
    """Station of radiko."""

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    list_program: Mapped[list[Program]] = relationship("Program", backref="station")
    transfer_target: Mapped[str | None] = mapped_column(String(255))

    def init(self, xml_parser: XmlParserStation) -> None:
        # Reason: "id" meets requirement of snake_case. pylint: disable=invalid-name
        self.id = xml_parser.id
        self.name = xml_parser.name

    @staticmethod
    def is_empty() -> bool:
        """Returns whether the station table is empty."""
        with SessionManager() as session:
            # Reason: Pylint's bug:
            # - `not-callable` false positive for class · Issue #8138 · pylint-dev/pylint
            #   https://github.com/pylint-dev/pylint/issues/8138
            count = cast("tuple[int]", session.query(func.count(Station.id)).one())  # pylint: disable=not-callable
            return count == (0,)


class Program(ModelInitByXml[XmlParserProgram]):
    """Program of radiko."""

    # Reason: Model. pylint: disable=too-many-instance-attributes
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    # The id in the radiko API is not unique...
    radiko_id: Mapped[str | None] = mapped_column(String(255))
    to: Mapped[datetime.datetime | None] = mapped_column(DATETIME)
    ft: Mapped[datetime.datetime | None] = mapped_column(DATETIME)
    title: Mapped[str | None] = mapped_column(String(255))
    station_id: Mapped[str] = mapped_column(String(255), ForeignKey("stations.id"), nullable=False)
    date: Mapped[datetime.date | None] = mapped_column(DATE)
    area_id: Mapped[str | None] = mapped_column(String(255))
    archive_status: Mapped[int | None] = mapped_column(INTEGER)

    def init(self, xml_parser: XmlParserProgram) -> None:
        # Reason: "id" meets requirement of snake_case.
        self.radiko_id = xml_parser.id  # pylint: disable=invalid-name
        # Reason: Can't understand what "ft" points.
        self.ft = xml_parser.ft  # pylint: disable=invalid-name
        # Reason: "to" meets requirement of snake_case.
        self.to = xml_parser.to  # pylint: disable=invalid-name
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
            session.commit()

    @property
    def ft_string(self) -> str:
        if not self.ft:
            message = f"{self.ft=}"
            raise ValueError(message)
        return RadikoDatetime.encode(self.ft)

    @property
    def to_string(self) -> str:
        if not self.to:
            message = f"{self.to=}"
            raise ValueError(message)
        return RadikoDatetime.encode(self.to)

    @staticmethod
    def is_empty(target_date: datetime.date) -> bool:
        with SessionManager() as session:
            count = cast("tuple[int]", session.query(func.count(Program.id)).filter(Program.date == target_date).one())  # pylint: disable=not-callable
            return count == (0,)

    @staticmethod
    def find(keywords: list[str]) -> list[Program]:
        """This method select Store model from database."""
        with SessionManager() as session:
            list_condition_keyword = [Program.title.like(f"%{keyword}%") for keyword in keywords]
            return (
                session.query(Program)
                .filter(
                    and_(or_(*list_condition_keyword), Program.archive_status.is_(ArchiveStatusId.ARCHIVABLE.value)),
                )
                .order_by(Program.ft.asc())
                .all()
            )

    @staticmethod
    def delete(boundary_date: datetime.date) -> None:
        with SessionManager() as session:
            session.query(Program).filter(Program.date < boundary_date).delete()

    def is_timefree30_required(self) -> bool:
        """Returns whether the program requires time-free 30-day download."""
        if not self.ft:
            message = f"{self.ft=}"
            raise ValueError(message)
        return RadikoDatetime.is_timefree30_required(self.ft)
