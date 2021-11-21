"""Stream spec factory."""
from logging import getLogger
from pathlib import Path

# noinspection PyPackageRequirements
import ffmpeg

# Reason: Following export method in __init__.py from Effective Python 2nd Edition item 85
from asyncffmpeg import StreamSpec  # type: ignore
from radikoplaylist import MasterPlaylistClient  # type: ignore
from radikoplaylist import TimeFreeMasterPlaylistRequest  # type: ignore

from radikopodcast.database.models import Program


class RadikoStreamSpecFactory:
    """Stream spec factory."""

    def __init__(self, program: Program):
        self.program = program
        self.logger = getLogger(__name__)

    async def create(self) -> StreamSpec:
        """Creates."""
        out_file_name = f"./output/{self.program.ft_string}_{self.program.station_id}_{self.program.title}.m4a"
        self.logger.debug("out file name: %s", out_file_name)
        if Path(out_file_name).exists():
            self.logger.error("File already exists. out_file_name = %s", out_file_name)
            raise FileExistsError(f"File already exists. {out_file_name=}")
        master_playlist_request = TimeFreeMasterPlaylistRequest(
            self.program.station_id, self.program.ft_string, self.program.to_string
        )
        master_playlist = MasterPlaylistClient.get(master_playlist_request, area_id=self.program.area_id)
        stream = ffmpeg.input(master_playlist.media_playlist_url, headers=master_playlist.headers, copytb="1")
        return ffmpeg.output(stream, out_file_name, f="mp4", c="copy")
