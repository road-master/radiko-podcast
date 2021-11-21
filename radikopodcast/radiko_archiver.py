"""Radiko Archiver."""
import asyncio
import os
from logging import getLogger

# Reason: Following export method in __init__.py from Effective Python 2nd Edition item 85
from asyncffmpeg import FFmpegCoroutineFactory  # type: ignore

from radikopodcast.database.models import Program
from radikopodcast.radiko_stream_spec_factory import RadikoStreamSpecFactory

TIME_TO_FORCE_TERMINATION = 8


class RadikoArchiver:
    """Radiko Archiver."""

    def __init__(
        self, *, time_to_force_termination: int = TIME_TO_FORCE_TERMINATION, stop_if_file_exists: bool = False
    ):
        self.ffmpeg_coroutine = FFmpegCoroutineFactory.create(time_to_force_termination=time_to_force_termination)
        self.stop_if_file_exists = stop_if_file_exists

    async def archive(self, program: Program) -> None:
        """Archives radiko program."""
        logger = getLogger(__name__)
        logger.debug("Start archive")
        logger.debug(
            "program time: %s, station: %s, start: %s, end: %s",
            program.title,
            program.station_id,
            program.ft,
            program.to,
        )
        try:
            program.mark_archiving()
            print(self.ffmpeg_coroutine)
            print(self.ffmpeg_coroutine.execute)
            await self.ffmpeg_coroutine.execute(RadikoStreamSpecFactory(program).create)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.debug("SIGINT for PID=%d", os.getpid())
            logger.debug("FFmpeg run cancelled.")
            program.mark_suspended()
            raise
        except FileExistsError:
            if self.stop_if_file_exists:
                raise
            program.mark_failed()
            return
        program.mark_archived()
