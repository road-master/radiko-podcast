"""Stream spec factory."""

from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

# noinspection PyPackageRequirements
import ffmpeg
from radikoplaylist import MasterPlaylistClient, TimeFreeMasterPlaylistRequest

if TYPE_CHECKING:
    from asyncffmpeg import StreamSpec

    from radikopodcast.database.models import Program


class RadikoStreamSpecFactory:
    """Stream spec factory."""

    def __init__(self, program: "Program") -> None:
        self.program = program
        if not self.program.area_id:
            message = f"{self.program.area_id=}"
            raise ValueError(message)
        self.area_id = self.program.area_id
        self.logger = getLogger(__name__)

    async def create(self) -> "StreamSpec":
        """Creates."""
        out_file_name = f"./output/{self.program.ft_string}_{self.program.station_id}_{self.program.title}.m4a"
        self.logger.debug("out file name: %s", out_file_name)
        if Path(out_file_name).exists():
            self.logger.error("File already exists. out_file_name = %s", out_file_name)
            message = f"File already exists. {out_file_name=}"
            raise FileExistsError(message)
        master_playlist_request = TimeFreeMasterPlaylistRequest(
            self.program.station_id,
            int(self.program.ft_string),
            int(self.program.to_string),
        )
        master_playlist = MasterPlaylistClient.get(master_playlist_request, area_id=self.area_id)
        stream = ffmpeg.input(master_playlist.media_playlist_url, headers=master_playlist.headers, copytb="1")
        return ffmpeg.output(stream, out_file_name, f="mp4", c="copy")
