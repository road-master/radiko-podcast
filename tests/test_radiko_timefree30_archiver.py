"""Tests for radiko_timefree30_archiver.py."""

from __future__ import annotations

import asyncio
from datetime import datetime
from textwrap import dedent
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import anyio
import pytest
from radikoplaylist import TimeFree30DayMasterPlaylistRequest

from radikopodcast.output_directory import OutputDirectory
from radikopodcast.programaggregate.segment.discovery import SegmentsDiscovery
from radikopodcast.programaggregate.segment.discovery import get_segment_datetimes
from radikopodcast.programaggregate.segment.downloader import SegmentsDownloader
from radikopodcast.programaggregate.timefree30 import RadikoProgramAggregateToArchiveTimeFree30
from radikopodcast.radiko_datetime import JST

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockFixture

    from radikopodcast.database.models import Program

_PLAYLIST_TEXT = dedent(
    """\
        #EXTM3U
        #EXTINF:5,
        https://example.com/20210116_050000_FMJ_001.aac
        #EXTINF:5,
        https://example.com/20210116_050005_FMJ_001.aac
        #EXT-X-ENDLIST
    """,
)


@pytest.fixture
def mock_aiohttp_session(mocker: MockFixture) -> MagicMock:
    """Mock aiohttp.ClientSession to return a canned media playlist."""
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.text = AsyncMock(return_value=_PLAYLIST_TEXT)
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=False)
    mock_session = MagicMock()
    mock_session.get.return_value = mock_response
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    return mocker.patch(
        "radikopodcast.programaggregate.segment.discovery.aiohttp.ClientSession",
        return_value=mock_session,
    )


class TestGetSegmentDatetimes:
    """Tests for get_segment_datetimes()."""

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("mock_master_playlist_client", "mock_aiohttp_session")
    async def test(self) -> None:
        """Should parse segment datetimes from AAC URL filenames."""
        result = await get_segment_datetimes(
            "FMJ",
            20210116050000,
            20210116050010,
            "JP13",
            "session_token",
            TimeFree30DayMasterPlaylistRequest,
        )
        assert result == [
            datetime(2021, 1, 16, 5, 0, 0, tzinfo=JST),
            datetime(2021, 1, 16, 5, 0, 5, tzinfo=JST),
        ]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("mock_master_playlist_client")
    async def test_ignores_non_aac_lines(self, mocker: MockFixture) -> None:
        """Should skip comment lines and non-AAC URLs."""
        playlist = dedent(
            """\
                #EXTM3U
                #EXT-X-TARGETDURATION:5
                https://example.com/20210116_050000_FMJ_001.aac
                #EXT-X-ENDLIST
            """,
        )
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = AsyncMock(return_value=playlist)
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mocker.patch(
            "radikopodcast.programaggregate.segment.discovery.aiohttp.ClientSession",
            return_value=mock_session,
        )
        result = await get_segment_datetimes(
            "FMJ",
            20210116050000,
            20210116050005,
            "JP13",
            "session_token",
            TimeFree30DayMasterPlaylistRequest,
        )
        assert result == [datetime(2021, 1, 16, 5, 0, 0, tzinfo=JST)]


class TestRadikoProgramAggregateToArchiveTimeFree30:
    """Tests for RadikoProgramAggregateToArchiveTimeFree30."""

    @pytest.mark.asyncio
    async def test(
        self,
        execution_environment: Path,
        model_program: Program,
        mocker: MockFixture,
        tmp_path: Path,
    ) -> None:
        """Archive() should discover segments, download them, and concatenate."""
        segment_dt = datetime(2021, 1, 16, 5, 0, 0, tzinfo=JST)
        mocker.patch.object(
            SegmentsDiscovery,
            "discover_all_segments",
            new=AsyncMock(return_value=[segment_dt]),
        )
        mocker.patch.object(
            SegmentsDownloader,
            "download",
            new=AsyncMock(return_value=anyio.Path(tmp_path / "input.txt")),
        )
        mock_ffmpeg_run = mocker.patch(
            "radikopodcast.programaggregate.slowapi.ffmpeg.run",
        )

        await RadikoProgramAggregateToArchiveTimeFree30(model_program, OutputDirectory(), "session_token").archive()

        mock_ffmpeg_run.assert_called_once()
        # Segment directory should be cleaned up
        assert not (execution_environment / "output" / OutputDirectory.build_file_stem(model_program)).exists()

    @pytest.mark.asyncio
    async def test_file_exists_error(
        self,
        execution_environment: Path,
        model_program: Program,
    ) -> None:
        """Archive() should raise FileExistsError when output file already exists."""
        out_file = (
            execution_environment
            / "output"
            / f"{model_program.ft_string}_{model_program.station_id}_{model_program.title}.m4a"
        )
        out_file.touch()
        with pytest.raises(FileExistsError):
            await RadikoProgramAggregateToArchiveTimeFree30(
                model_program,
                OutputDirectory(),
                "session_token",
            ).archive()

    @staticmethod
    @pytest.mark.usefixtures("execution_environment")
    def test_area_id_none(model_program_area_id_none: Program) -> None:
        """Archive() should raise ValueError when area_id is None."""
        with pytest.raises(ValueError, match="None"):
            asyncio.run(
                RadikoProgramAggregateToArchiveTimeFree30(
                    model_program_area_id_none,
                    OutputDirectory(),
                    "session_token",
                ).archive(),
            )

    @pytest.mark.asyncio
    async def test_segment_dir_cleaned_up_on_error(
        self,
        execution_environment: Path,
        model_program: Program,
        mocker: MockFixture,
    ) -> None:
        """Archive() should clean up the segment directory even if an error occurs."""
        mocker.patch.object(
            SegmentsDiscovery,
            "discover_all_segments",
            new=AsyncMock(side_effect=RuntimeError("discovery failed")),
        )

        with pytest.raises(RuntimeError):
            await RadikoProgramAggregateToArchiveTimeFree30(
                model_program,
                OutputDirectory(),
                "session_token",
            ).archive()

        assert not (execution_environment / "output" / OutputDirectory.build_file_stem(model_program)).exists()
