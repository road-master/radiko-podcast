"""Radiko Archiver."""

from __future__ import annotations

import asyncio
import os
from logging import getLogger
from typing import TYPE_CHECKING

from radikoplaylist.exceptions import BadHttpStatusCodeError
from radikoplaylist.exceptions import NoAvailableUrlError
from requests.exceptions import ConnectionError as RequestsConnectionError

if TYPE_CHECKING:
    from radikopodcast.database.models import Program
    from radikopodcast.programaggregate.factory import RadikoProgramAggregateToArchiveFactory

_ARCHIVE_ERROR_MESSAGES: dict[type[Exception], str] = {
    BadHttpStatusCodeError: (
        "HTTP error archiving %s %s — station may not support this time-free type; marking failed."
    ),
    NoAvailableUrlError: "No available playlist URL for %s %s — URL may be unsupported; marking failed.",
    RequestsConnectionError: "Connection error archiving %s %s — Radiko API unreachable; marking failed.",
}


class RadikoArchiveWorkflow:
    """Workflow for archiving Radiko programs, handling both normal and 30-day time-free cases."""

    def __init__(
        self,
        radiko_program_aggregate_factory: RadikoProgramAggregateToArchiveFactory,
        *,
        stop_if_file_exists: bool = False,
    ) -> None:
        self.logger = getLogger(__name__)
        self.radiko_program_aggregate_factory = radiko_program_aggregate_factory
        self.stop_if_file_exists = stop_if_file_exists

    async def execute(self, program: Program) -> None:
        """Archive radiko program."""
        self.logger.debug("Start archive")
        self.logger.debug(
            "program time: %s, station: %s, start: %s, end: %s",
            program.title,
            program.station_id,
            program.ft,
            program.to,
        )
        program.mark_archiving()
        try:
            await self._try_archive(program)
        except FileExistsError:
            if self.stop_if_file_exists:
                raise
            program.mark_failed()
            return
        except (BadHttpStatusCodeError, NoAvailableUrlError, RequestsConnectionError):
            return
        program.mark_archived()

    async def _try_archive(self, program: Program) -> None:
        try:
            radiko_program_aggregate = self.radiko_program_aggregate_factory.create(program)
            await radiko_program_aggregate.archive()
        except (KeyboardInterrupt, asyncio.CancelledError):
            self.logger.debug("SIGINT for PID=%d", os.getpid())
            self.logger.debug("FFmpeg run cancelled.")
            program.mark_suspended()
            raise
        except (BadHttpStatusCodeError, NoAvailableUrlError, RequestsConnectionError) as error:
            self.logger.warning(
                _ARCHIVE_ERROR_MESSAGES[type(error)],
                program.station_id,
                program.ft_string,
            )
            program.mark_failed()
            raise
