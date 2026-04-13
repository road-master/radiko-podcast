"""Segment downloader for Radiko time-free archiving."""

from __future__ import annotations

import asyncio
from datetime import datetime
from datetime import timedelta
from logging import getLogger
from typing import TYPE_CHECKING

import ffmpeg
from asynccpu import ProcessTaskPoolExecutor
from radikoplaylist import MasterPlaylistClient
from radikoplaylist import TimeFree30DayMasterPlaylistRequest

from radikopodcast.radiko_datetime import RadikoDatetime

if TYPE_CHECKING:
    import anyio

    from radikopodcast.programaggregate.timefree30.segment_directory import SegmentDirectory

_MAX_WORKERS = 3
_SEGMENT_DURATION_SECONDS = 5


class SegmentsDownloader:
    """Downloads segments in parallel using ffmpeg and ProcessTaskPoolExecutor."""

    def __init__(self, station_id: str, area_id: str, radiko_session: str, segment_dir: SegmentDirectory) -> None:
        self.station_id = station_id
        self.area_id = area_id
        self.radiko_session = radiko_session
        self.segment_dir = segment_dir
        self.logger = getLogger(__name__)

    async def download(self, segment_dts: list[datetime]) -> anyio.Path:
        with ProcessTaskPoolExecutor(max_workers=_MAX_WORKERS, cancel_tasks_when_shutdown=True) as executor:
            awaitables = [executor.create_process_task(self.download_segment, dt) for dt in segment_dts]
            await asyncio.gather(*awaitables)
        return await self.segment_dir.create_segment_list_file()

    async def download_segment(self, segment_dt: datetime) -> None:
        """Downloads one 5-second segment as an .m4a file into segment_dir."""
        start_at = int(segment_dt.strftime(RadikoDatetime.FORMAT_CODE))
        end_at = int((segment_dt + timedelta(seconds=4)).strftime(RadikoDatetime.FORMAT_CODE))
        master_playlist_request = TimeFree30DayMasterPlaylistRequest(self.station_id, start_at, end_at)
        master_playlist = MasterPlaylistClient.get(
            master_playlist_request,
            area_id=self.area_id,
            radiko_session=self.radiko_session,
        )
        stream = ffmpeg.input(
            master_playlist.media_playlist_url,
            headers=master_playlist.headers,
            reconnect=1,
            reconnect_streamed=1,
            reconnect_delay_max=30,
            seg_max_retry=1000,
        )
        stream = ffmpeg.output(
            stream,
            str(self.segment_dir.get_segment_path(segment_dt)),
            f="mp4",
            c="copy",
            movflags="+faststart",
            t=_SEGMENT_DURATION_SECONDS,
        )
        ffmpeg.run(stream)
