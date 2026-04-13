"""Radiko program aggregate archiver classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from radikopodcast.programaggregate.base import RadikoProgramAggregateToArchive
from radikopodcast.radiko_stream_spec_factory import RadikoStreamSpecFactory

if TYPE_CHECKING:
    from asyncffmpeg import FFmpegCoroutine
    from asyncffmpeg import FFmpegProcess

    from radikopodcast.database.models import Program
    from radikopodcast.output_directory import OutputDirectory

TIME_TO_FORCE_TERMINATION = 8


class RadikoProgramAggregateToArchiveGeneral(RadikoProgramAggregateToArchive):
    """Archiver for normal (non-time-free-30) programs, which uses ffmpeg to record the stream directly."""

    def __init__(
        self,
        program: Program,
        output_directory: OutputDirectory,
        ffmpeg_coroutine: FFmpegCoroutine[FFmpegProcess],
    ) -> None:
        super().__init__(program, output_directory)
        self.ffmpeg_coroutine = ffmpeg_coroutine

    async def archive(self) -> None:
        await self.ffmpeg_coroutine.execute(RadikoStreamSpecFactory(self.program, self.output_directory).create)
