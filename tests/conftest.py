"""Configuration of pytest"""
import os
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from shutil import copyfile
from typing import Generator, List, Optional, Tuple, Type
from unittest.mock import AsyncMock, MagicMock, Mock
from xml.etree import ElementTree

import pytest
from _pytest.fixtures import FixtureRequest
from asyncffmpeg.ffmpeg_coroutine_factory import FFmpegCoroutineFactory
from click.testing import CliRunner
from jinja2 import Template
from pytest_mock import MockFixture
from radikoplaylist.master_playlist_client import MasterPlaylistClient
from requests_mock.mocker import Mocker
from sqlalchemy.orm.session import Session as SQLAlchemySession

from radikopodcast.database.models import Program
from radikopodcast.radikoxml.xml_converter import XmlConverterProgram
from tests.test_radiko_stream_spec_factory import MasterPlaylist
from tests.testlibraries.database_for_test import DatabaseForTest

collect_ignore = ["setup.py"]


@pytest.fixture
def config_yaml(resource_path_root: Path) -> Generator[Path, None, None]:
    yield resource_path_root / "config.yml"


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def execution_environment(tmp_path: Path, config_yaml: Path, request: FixtureRequest) -> Generator[Path, None, None]:
    """Move to temporary directory with ./config.yml and ./output/ directory."""
    copyfile(config_yaml, tmp_path / "config.yml")
    (tmp_path / "output").mkdir()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(request.config.invocation_dir)


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def runner_in_isolated_filesystem(tmp_path: Path, config_yaml: Path) -> Generator[CliRunner, None, None]:
    """CLI runner in isolated filesystem with ./config.yml and ./output/ directory."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as isolated_filesystem:
        copyfile(config_yaml, Path(isolated_filesystem) / "config.yml")
        (tmp_path / "output").mkdir()
        yield runner


@pytest.fixture
def xml_program(resource_path_root: Path) -> Generator[str, None, None]:
    yield (resource_path_root / "program.xml").read_text(encoding="utf-8")


@pytest.fixture
def xml_station(resource_path_root: Path) -> Generator[str, None, None]:
    yield (resource_path_root / "station.xml").read_text(encoding="utf-8")


@pytest.fixture
def xml_station_name_lacked() -> Generator[str, None, None]:
    yield """<stations area_id="JP13" area_name="TOKYO JAPAN">
<station><id>TBS</id></station>
</stations>"""


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def mock_requests_program(requests_mock: Mocker, xml_program: str) -> None:
    requests_mock.get(
        "http://radiko.jp/v3/program/date/20210116/JP13.xml", text=xml_program,
    )


@dataclass
class GenreForXml:
    id: str  # Reason: To follow specification of radiko. pylint: disable=invalid-name
    name: str


@dataclass
class ProgramForXml:
    """To render xml for test

    since putting static xml file for test into Git repository causes increasement of repository file size.
    """

    # Reason: Model. pylint: disable=too-many-instance-attributes
    id: str  # Reason: To follow specification of radiko. pylint: disable=invalid-name
    ft: datetime  # Reason: To follow specification of radiko. pylint: disable=invalid-name
    to: datetime  # Reason: To follow specification of radiko. pylint: disable=invalid-name
    title: str
    url: str = ""
    description: str = ""
    information: str = ""
    performer: str = ""
    image: str = ""
    tags: List[str] = field(default_factory=list)
    genre_personality: Optional[GenreForXml] = None
    genre_program: Optional[GenreForXml] = None

    @property
    def ftl(self) -> str:
        return self.ft.strftime("%H%M")

    @property
    def tol(self) -> str:
        return self.to.strftime("%H%M")

    @property
    def duration(self) -> str:
        return str((self.to - self.ft).total_seconds())


@dataclass
class StationForXml:
    id: str  # Reason: To follow specification of radiko. pylint: disable=invalid-name
    name: str
    date: date
    list_program: List[ProgramForXml]


def create_list_station(index: int) -> List[StationForXml]:
    return [
        StationForXml(
            "FMJ",
            "J-WAVE",
            date(2021, 1, 10 + index),
            [
                ProgramForXml(
                    "1234567890",
                    datetime(2021, 1, 10 + index, 5, 0, 0),
                    datetime(2021, 1, 10 + index, 6, 0, 0),
                    "title",
                    "https://www.j-wave.co.jp/original/title/",
                    "description",
                    "information",
                    "performer",
                    "https://radiko.jp/res/program/DEFAULT_IMAGE/FMJ/abcdefghij.jpg",
                    [],
                    None,
                    GenreForXml("A012", "プログラム",),
                )
            ],
        )
    ]


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def mock_requests_program_week(resource_path_root: Path, requests_mock: Mocker, xml_program: str) -> None:
    """Mock radiko API for getting program list for 1 week."""
    template = Template((resource_path_root / "program.xml.jinja").read_text(encoding="utf-8"))
    list_xml_program = [
        template.render(list_station=create_list_station(0)),
        template.render(list_station=create_list_station(1)),
        template.render(list_station=create_list_station(2)),
        template.render(list_station=create_list_station(3)),
        template.render(list_station=create_list_station(4)),
        template.render(list_station=create_list_station(5)),
        xml_program,
    ]
    for index, program in enumerate(list_xml_program):
        program_date = 10 + index
        requests_mock.get(
            f"http://radiko.jp/v3/program/date/202101{program_date}/JP13.xml", text=program,
        )


@pytest.fixture
def mock_master_playlist_client(mocker: MockFixture) -> Generator[MagicMock, None, None]:
    """Mock MasterPlaylistClient.get()."""
    master_playlist = MasterPlaylist(
        "",
        {
            "Accept": "*/*",
            "Connection": "keep-alive",
            "User-Agent": "python3.7",
            "X-Radiko-App": "pc_html5",
            "X-Radiko-App-Version": "0.0.1",
            "X-Radiko-AreaId": "JP13",
            "X-Radiko-AuthToken": "HrUNR0zyrGseqvlPl1-khQ",
            "X-Radiko-Device": "pc",
            "X-Radiko-Partialkey": b"ZTFlZjJmZDY2YzMyMjA5ZA==",
            "X-Radiko-User": "dummy_user",
        },
    )
    mock_get = mocker.MagicMock(return_value=master_playlist)
    mocker.patch.object(MasterPlaylistClient, "get", mock_get)
    yield mock_get


class PicklableMock(Mock):
    """see: https://github.com/testing-cabal/mock/issues/139#issuecomment-122128815"""

    def __reduce__(self) -> Tuple[Type[Mock], Tuple[()]]:
        return (Mock, ())


@pytest.fixture
def mock_ffmpeg_coroutine(mocker: MockFixture) -> Generator[PicklableMock, None, None]:
    """Mock FFmpegCroutine."""
    mock = PicklableMock()
    # Reason: To init original mock. pylint: disable=attribute-defined-outside-init
    mock.execute = AsyncMock()
    mocker.patch.object(FFmpegCoroutineFactory, "create", mock)
    yield mock


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def mock_requests_station(requests_mock: Mocker, xml_station: str) -> None:
    requests_mock.get(
        "http://radiko.jp/v3/station/list/JP13.xml", text=xml_station,
    )


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def element_tree_program(xml_program: str) -> Generator[ElementTree.Element, None, None]:
    yield ElementTree.fromstring(xml_program)


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def element_tree_station(xml_station: str) -> Generator[ElementTree.Element, None, None]:
    yield ElementTree.fromstring(xml_station)


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def model_program(element_tree_program: ElementTree.Element) -> Generator[Program, None, None]:
    yield XmlConverterProgram(date(2021, 1, 16), element_tree_program, "JP13").to_model()[0]


@pytest.fixture
def database_session() -> Generator[SQLAlchemySession, None, None]:
    """This fixture prepares database and fixture records."""
    yield from DatabaseForTest.database_session()


@pytest.fixture
def database_session_with_schema() -> Generator[SQLAlchemySession, None, None]:
    """This fixture prepares database session and fixture records to reset database after each test."""
    yield from DatabaseForTest.database_session_with_schema()


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=redefined-outer-name
def record_program(
    database_session_with_schema: SQLAlchemySession, element_tree_program: ElementTree.Element
) -> Generator[SQLAlchemySession, None, None]:
    """This fixture prepares database session and fixture records to reset database after each test."""
    Program.save_all(XmlConverterProgram(date(2021, 1, 16), element_tree_program, "JP13").to_model())
    database_session_with_schema.flush()
    yield database_session_with_schema


@pytest.fixture
# Reason: To refer other fixture. pylint: disable=unused-argument,redefined-outer-name
def mock_all(
    database_session: SQLAlchemySession,
    mock_requests_station: None,
    mock_requests_program_week: None,
    mock_master_playlist_client: MagicMock,
    mock_ffmpeg_coroutine: PicklableMock,
) -> Generator[None, None, None]:
    """Set of mocks for E2E test."""
    yield
