"""Output directory management for Radiko podcast archiving."""

from logging import getLogger
from pathlib import Path

import anyio
from pathvalidate import sanitize_filename

from radikopodcast.database.models import Program


class OutputDirectory:
    """Output directory."""

    def __init__(self) -> None:
        self.logger = getLogger(__name__)
        self.path = Path("output")
        self.path.mkdir(exist_ok=True)

    async def get_output_file_path(self, program: Program) -> anyio.Path:
        """Returns output file path for the given program."""
        file_name = f"{self.build_file_stem(program)}.m4a"
        output_file_path = anyio.Path(self.path) / file_name
        self.logger.debug("out file name: %s", output_file_path)
        if await output_file_path.exists():
            self.logger.error("File already exists. out_file_name = %s", output_file_path)
            message = f"File already exists. {output_file_path=}"
            raise FileExistsError(message)
        return output_file_path

    @staticmethod
    def build_file_stem(program: Program) -> str:
        """Builds file stem for the given program."""
        return f"{program.ft_string}_{program.station_id}_{sanitize_filename(str(program.title))}"
