# Copyright (C) 2026 Master
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

MAX_ARCHIVE_RETRY_COUNT = 5


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
        except NoAvailableUrlError as error:
            self.logger.warning(
                "No available playlist URL for %s %s: %s — the station may not support this URL type; marking failed.",
                program.station_id,
                program.ft_string,
                error,
            )
            program.mark_failed()
            raise
        except (BadHttpStatusCodeError, RequestsConnectionError) as error:
            self._retry_or_fail(program, error)
            raise

    def _retry_or_fail(self, program: Program, error: Exception) -> None:
        """Requeue the program for transient errors; mark failed once retries are exhausted."""
        retry_count = program.mark_retry_or_failed(MAX_ARCHIVE_RETRY_COUNT)
        if retry_count < MAX_ARCHIVE_RETRY_COUNT:
            self.logger.warning(
                "Transient error archiving %s %s: %s (attempt %d/%d, will retry next cycle)",
                program.station_id,
                program.ft_string,
                error,
                retry_count,
                MAX_ARCHIVE_RETRY_COUNT,
            )
            return
        self.logger.error(
            "Giving up archiving %s %s after %d attempts: %s",
            program.station_id,
            program.ft_string,
            retry_count,
            error,
        )
