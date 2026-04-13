"""Radiko Archiver."""

from __future__ import annotations

import asyncio
import os
from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from radikopodcast.database.models import Program
    from radikopodcast.programaggregate.factory import RadikoProgramAggregateToArchiveFactory


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
        """Archives radiko program."""
        self.logger.debug("Start archive")
        self.logger.debug(
            "program time: %s, station: %s, start: %s, end: %s",
            program.title,
            program.station_id,
            program.ft,
            program.to,
        )
        try:
            program.mark_archiving()
            radiko_program_aggregate = self.radiko_program_aggregate_factory.create(program)
            await radiko_program_aggregate.archive()
        except (KeyboardInterrupt, asyncio.CancelledError):
            self.logger.debug("SIGINT for PID=%d", os.getpid())
            self.logger.debug("FFmpeg run cancelled.")
            program.mark_suspended()
            raise
        except FileExistsError:
            if self.stop_if_file_exists:
                raise
            program.mark_failed()
            return
        program.mark_archived()
