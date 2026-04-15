"""Radiko program aggregate archiver for slow (non-radiko.jp) API endpoints."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

import ffmpeg

from radikopodcast.programaggregate.base import RadikoProgramAggregateToArchive
from radikopodcast.programaggregate.segment.directory import SegmentDirectory
from radikopodcast.programaggregate.segment.discovery import SegmentsDiscovery
from radikopodcast.programaggregate.segment.downloader import SegmentsDownloader

if TYPE_CHECKING:
    from radikopodcast.database.models import Program
    from radikopodcast.output_directory import OutputDirectory
    from radikopodcast.programaggregate.segment.discovery import MasterPlaylistRequestFactory


class RadikoProgramAggregateToArchiveSlowApi(RadikoProgramAggregateToArchive):
    """Program aggregate for stations served from non-radiko.jp (slow) API endpoints.

    Uses segment-by-segment download: discovers all 5-second segments in parallel,
    downloads each one independently, then concatenates into a single .m4a file.
    The request_factory controls which playlist API type (type=b or type=c) is used.
    """

    def __init__(
        self,
        program: Program,
        output_directory: OutputDirectory,
        radiko_session: str,
        request_factory: MasterPlaylistRequestFactory,
    ) -> None:
        super().__init__(program, output_directory)
        self.logger = getLogger(__name__)
        self.radiko_session = radiko_session
        self.request_factory = request_factory

    async def archive(self) -> None:
        """Archives a program via segment-by-segment download and ffmpeg concatenation."""
        out_file = await self.output_directory.get_output_file_path(self.program)
        area_id = self.program.area_id
        if not area_id:
            message = f"{self.program.area_id=}"
            raise ValueError(message)
        async with SegmentDirectory(self.output_directory, self.program) as segment_dir:
            segment_discovery = SegmentsDiscovery(self.program, area_id, self.radiko_session, self.request_factory)
            downloader = SegmentsDownloader(
                self.program.station_id,
                area_id,
                self.radiko_session,
                segment_dir,
                self.request_factory,
            )
            all_segment_dts = await segment_discovery.discover_all_segments()
            self.logger.debug("Discovered %d segments for %s", len(all_segment_dts), self.program.title)
            input_list_path = await downloader.download(all_segment_dts)
            stream = ffmpeg.input(str(input_list_path), f="concat", safe=0)
            stream = ffmpeg.output(stream, str(out_file), f="mp4", c="copy", movflags="+faststart")
            ffmpeg.run(stream)
