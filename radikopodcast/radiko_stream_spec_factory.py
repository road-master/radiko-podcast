"""Stream spec factory."""

from logging import getLogger
from typing import TYPE_CHECKING

# noinspection PyPackageRequirements
import ffmpeg
from radikoplaylist import MasterPlaylistClient
from radikoplaylist import TimeFreeMasterPlaylistRequest

if TYPE_CHECKING:
    from asyncffmpeg import StreamSpec

    from radikopodcast.database.models import Program
    from radikopodcast.output_directory import OutputDirectory


class RadikoStreamSpecFactory:
    """Stream spec factory."""

    def __init__(self, program: "Program", output_directory: "OutputDirectory") -> None:
        self.program = program
        self.output_directory = output_directory
        if not self.program.area_id:
            message = f"{self.program.area_id=}"
            raise ValueError(message)
        self.area_id = self.program.area_id
        self.logger = getLogger(__name__)

    async def create(self) -> "StreamSpec":
        """Creates."""
        master_playlist_request = TimeFreeMasterPlaylistRequest(
            self.program.station_id,
            int(self.program.ft_string),
            int(self.program.to_string),
        )
        master_playlist = MasterPlaylistClient.get(master_playlist_request, area_id=self.area_id)
        stream = ffmpeg.input(master_playlist.media_playlist_url, headers=master_playlist.headers, copytb="1")
        return ffmpeg.output(
            stream,
            str(await self.output_directory.get_output_file_path(self.program)),
            f="mp4",
            c="copy",
        )
