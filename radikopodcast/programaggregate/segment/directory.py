"""Segment directory context manager for Radiko time-free archiving."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

import anyio
from typing_extensions import Self

from radikopodcast.radiko_datetime import RadikoDatetime

if TYPE_CHECKING:
    from datetime import datetime
    from types import TracebackType

    from radikopodcast.database.models import Program
    from radikopodcast.output_directory import OutputDirectory


class SegmentDirectory:
    """Context manager for segment directory, ensuring cleanup after use."""

    def __init__(self, output_directory: OutputDirectory, program: Program) -> None:
        self.output_directory = output_directory
        self.program = program
        self.path = anyio.Path(output_directory.path / output_directory.build_file_stem(program))

    async def __aenter__(self) -> Self:
        await self.path.mkdir(parents=True, exist_ok=True)
        return self

    async def __aexit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        shutil.rmtree(self.path, ignore_errors=True)

    async def create_segment_list_file(self) -> anyio.Path:
        segment_files = sorted([f async for f in self.path.glob("*.m4a")])
        input_list_path = self.path / "input.txt"
        await input_list_path.write_text("\n".join(f"file '{f.name}'" for f in segment_files), encoding="utf-8")
        return input_list_path

    def get_segment_path(self, segment_dt: datetime) -> anyio.Path:
        return self.path / f"{segment_dt.strftime(RadikoDatetime.FORMAT_CODE)}.m4a"
