"""Tests for radiko_stream_spec_factory.py."""

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

# Reason: Maybe, requires to update ffmpeg-python side.
from ffmpeg.nodes import Stream  # type: ignore[import-untyped]
import pytest

from radikopodcast.radiko_stream_spec_factory import RadikoStreamSpecFactory

if TYPE_CHECKING:
    from pathlib import Path

    from radikopodcast.database.models import Program


@dataclass
class MasterPlaylist:
    media_playlist_url: str
    headers: dict[str, Any]


class TestRadikoStreamSpecFactory:
    """Tests for RadikoStreamSpecFactory."""

    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("mock_master_playlist_client")
    async def test(self, model_program: "Program") -> None:
        """Function create() should create stream spec."""
        radiko_stream_spec_factory = RadikoStreamSpecFactory(model_program)
        stream_spec = await radiko_stream_spec_factory.create()
        assert isinstance(stream_spec, Stream)
        self.check_stream_spec(stream_spec)

    def check_stream_spec(self, stream_spec: Stream) -> None:
        assert "output(c='copy', filename='./output/20210116050000_FMJ_ZAPPA.m4a', format='mp4')[None]" in str(
            stream_spec,
        )
        assert stream_spec.node.short_repr == "20210116050000_FMJ_ZAPPA.m4a"
        assert stream_spec.label is None
        assert stream_spec.selector is None

    @staticmethod
    def test_area_id_none(model_program_area_id_none: "Program") -> None:
        with pytest.raises(ValueError, match="None") as excinfo:
            RadikoStreamSpecFactory(model_program_area_id_none)
        assert "None" in str(excinfo.value)

    @staticmethod
    @pytest.mark.asyncio()
    @pytest.mark.usefixtures("mock_master_playlist_client")
    async def test_file_exists_error(execution_environment: "Path", model_program: "Program") -> None:
        """Method: create() should raise FileExistsError when output file already exists."""
        (execution_environment / "output" / "20210116050000_FMJ_ZAPPA.m4a").touch()
        radiko_stream_spec_factory = RadikoStreamSpecFactory(model_program)
        with pytest.raises(FileExistsError):
            await radiko_stream_spec_factory.create()
