"""Radiko program archiver base class."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from radikopodcast.database.models import Program
    from radikopodcast.output_directory import OutputDirectory


class RadikoProgramAggregateToArchive:
    def __init__(self, program: Program, output_directory: OutputDirectory) -> None:
        self.program = program
        self.output_directory = output_directory

    async def archive(self) -> None:
        raise NotImplementedError
