"""Radiko program aggregate archiver factory."""

from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from asyncffmpeg import FFmpegCoroutineFactory

from radikopodcast.programaggregate.normal import TIME_TO_FORCE_TERMINATION
from radikopodcast.programaggregate.normal import RadikoProgramAggregateToArchiveGeneral
from radikopodcast.programaggregate.timefree30 import RadikoProgramAggregateToArchiveTimeFree30

if TYPE_CHECKING:
    from radikopodcast.database.models import Program
    from radikopodcast.output_directory import OutputDirectory
    from radikopodcast.programaggregate.base import RadikoProgramAggregateToArchive


class RadikoProgramAggregateToArchiveFactory:
    """Factory for RadikoProgramArchiver."""

    def __init__(
        self,
        output_directory: OutputDirectory,
        *,
        time_to_force_termination: int = TIME_TO_FORCE_TERMINATION,
        radiko_session: str | None = None,
    ) -> None:
        self.logger = getLogger(__name__)
        self.output_directory = output_directory
        self.ffmpeg_coroutine = FFmpegCoroutineFactory.create(time_to_force_termination=time_to_force_termination)
        self.logger.info(self.ffmpeg_coroutine)
        self.logger.info(self.ffmpeg_coroutine.execute)
        self.radiko_session = radiko_session

    def create(self, program: Program) -> RadikoProgramAggregateToArchive:
        if self.radiko_session and program.is_timefree30_required():
            return RadikoProgramAggregateToArchiveTimeFree30(program, self.output_directory, self.radiko_session)
        return RadikoProgramAggregateToArchiveGeneral(program, self.output_directory, self.ffmpeg_coroutine)
