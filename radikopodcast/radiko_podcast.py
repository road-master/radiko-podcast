"""Main module."""
import asyncio
import logging
import queue
from logging import LogRecord
from pathlib import Path
from typing import Any, Callable, Optional

# Reason: Following export method in __init__.py from Effective Python 2nd Edition item 85
from asynccpu import ProcessTaskPoolExecutor  # type: ignore

from radikopodcast import CONFIG
from radikopodcast.database.program_schedule import ProgramSchedule
from radikopodcast.radiko_archiver import TIME_TO_FORCE_TERMINATION, RadikoArchiver


class RadikoPodcast:
    """Main class."""

    def __init__(
        self,
        *,
        path_to_configuration: Optional[Path] = None,
        time_to_force_termination: int = TIME_TO_FORCE_TERMINATION,
        # Reason: This argument name is API. pylint: disable=redefined-outer-name
        queue: Optional[queue.Queue[LogRecord]] = None,
        configurer: Optional[Callable[[], Any]] = None,
    ) -> None:
        logging.basicConfig(level=logging.DEBUG)
        # Reason Yaml Dataclass Config's bug.
        CONFIG.load(path_to_configuration)  # type: ignore
        self.radiko_archiver = RadikoArchiver(
            time_to_force_termination=time_to_force_termination, stop_if_file_exists=CONFIG.stop_if_file_exists
        )
        self.queue = queue
        self.configurer = configurer
        self.program_schedule = ProgramSchedule(area_id=CONFIG.area_id)
        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        """Runs"""
        try:
            asyncio.run(self.archive_repeatedly())
        except Exception as error:
            self.logger.exception(error)
            raise

    async def archive_repeatedly(self) -> None:
        """Archives repeatedly."""
        with ProcessTaskPoolExecutor(
            max_workers=CONFIG.number_process,
            cancel_tasks_when_shutdown=True,
            queue=self.queue,
            configurer=self.configurer,
        ) as executor:
            while True:
                self.program_schedule.download_if_program_has_not_been_downloaded()
                for program in self.program_schedule.search(CONFIG.keywords):
                    self.logger.debug("Start: program.title = %s", program.title)
                    # Reason: pylint bug. pylint: disable=no-member
                    executor.create_process_task(self.radiko_archiver.archive, program)
                    self.logger.debug("Finish: program.title = %s", program.title)
                await self.sleep(180)

    @staticmethod
    async def sleep(second: float) -> None:
        await asyncio.sleep(second)
