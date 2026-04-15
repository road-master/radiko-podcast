"""Radiko segment discovery via the time-free endpoint."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Callable
from datetime import datetime
from datetime import timedelta
from logging import getLogger
from typing import TYPE_CHECKING

import aiohttp
from asynccpu import ProcessTaskPoolExecutor
from radikoplaylist import MasterPlaylistClient
from radikoplaylist import TimeFree30DayMasterPlaylistRequest
from radikoplaylist.master_playlist_request import MasterPlaylistRequest

from radikopodcast.radiko_datetime import JST
from radikopodcast.radiko_datetime import RadikoDatetime

if TYPE_CHECKING:
    from collections.abc import Generator

    from radikoplaylist.master_playlist import MasterPlaylist

    from radikopodcast.database.models import Program

MasterPlaylistRequestFactory = Callable[[str, int, int], MasterPlaylistRequest]

_INTERVAL_SECONDS = 5
_MAX_WORKERS = 3


class MediaPlaylistText:
    """Represents the text content of a media playlist and provides methods to analyze it."""

    AAC_SEGMENT_PATTERN = re.compile(r"/(\d{8}_\d{6})_[^/]+\.aac$")

    def __init__(self, string: str) -> None:
        self.string = string

    def analyze_urls(self) -> Generator[str]:
        """Parses segment datetimes from AAC URLs in media playlist text."""
        lines = (line.strip() for line in self.string.splitlines())
        return (line for line in lines if line and not line.startswith("#"))

    def analyze_segment_datetimes(self) -> list[datetime]:
        """Parses segment datetimes from AAC URLs in media playlist text."""
        matches = (match for url in self.analyze_urls() if (match := self.AAC_SEGMENT_PATTERN.search(url)))
        return [datetime.strptime(m.group(1), "%Y%m%d_%H%M%S").replace(tzinfo=JST) for m in matches]


async def fetch_media_playlist_text(master_playlist: MasterPlaylist) -> MediaPlaylistText:
    """Fetches media playlist text from the URL in master_playlist using aiohttp."""
    async with (
        aiohttp.ClientSession() as session,
        session.get(
            master_playlist.media_playlist_url,
            headers={k: v.decode() if isinstance(v, bytes) else v for k, v in master_playlist.headers.items()},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response,
    ):
        response.raise_for_status()
        return MediaPlaylistText(await response.text())


# Reason: Top-level function required for pickling in ProcessTaskPoolExecutor; all context must be explicit args.
async def get_segment_datetimes(  # noqa: PLR0913 pylint: disable=too-many-arguments, too-many-positional-arguments
    station_id: str,
    start_at: int,
    end_at: int,
    area_id: str,
    radiko_session: str,
    request_factory: MasterPlaylistRequestFactory,
) -> list[datetime]:
    """Fetches media playlist and returns the segment datetimes parsed from AAC URLs."""
    master_playlist_request = request_factory(station_id, start_at, end_at)
    master_playlist = MasterPlaylistClient.get(master_playlist_request, area_id=area_id, radiko_session=radiko_session)
    text = await fetch_media_playlist_text(master_playlist)
    return text.analyze_segment_datetimes()


class SegmentsDiscovery:
    """Discovers all segment datetimes for a program via the time-free endpoint."""

    def __init__(
        self,
        program: Program,
        area_id: str,
        radiko_session: str,
        request_factory: MasterPlaylistRequestFactory = TimeFree30DayMasterPlaylistRequest,
    ) -> None:
        self.program = program
        self.area_id = area_id
        self.radiko_session = radiko_session
        self.request_factory = request_factory
        self.logger = getLogger(__name__)

    async def discover_all_segments(self) -> list[datetime]:
        results = await self.gather_segment_datetimes()
        return sorted({dt for result in results for dt in result})

    def create_chunks(self) -> list[tuple[datetime, datetime]]:
        """Creates chunks of the program's time range to query for segments in parallel."""
        dt_start = datetime.strptime(self.program.ft_string, RadikoDatetime.FORMAT_CODE).replace(tzinfo=JST)
        dt_end = datetime.strptime(self.program.to_string, RadikoDatetime.FORMAT_CODE).replace(tzinfo=JST)
        chunk = timedelta(seconds=_INTERVAL_SECONDS)
        chunks: list[tuple[datetime, datetime]] = []
        current = dt_start
        while current < dt_end:
            next_dt = min(dt_end, current + chunk)
            chunks.append((current, next_dt))
            current = next_dt
        return chunks

    async def gather_segment_datetimes(self) -> list[list[datetime]]:
        """Fetches segment datetimes for all chunks in parallel using ProcessTaskPoolExecutor."""
        chunks = self.create_chunks()
        with ProcessTaskPoolExecutor(max_workers=_MAX_WORKERS, cancel_tasks_when_shutdown=True) as executor:
            awaitables = {
                executor.create_process_task(
                    get_segment_datetimes,
                    self.program.station_id,
                    int(start.strftime(RadikoDatetime.FORMAT_CODE)),
                    int(end.strftime(RadikoDatetime.FORMAT_CODE)),
                    self.area_id,
                    self.radiko_session,
                    self.request_factory,
                )
                for start, end in chunks
            }
            return await asyncio.gather(*awaitables)
