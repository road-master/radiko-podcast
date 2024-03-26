"""Test for radiko_archiver.py."""

import asyncio
import sys
from unittest.mock import AsyncMock

from asynccpu.process_task_pool_executor import ProcessTaskPoolExecutor
from asyncffmpeg import FFmpegCoroutine, FFmpegCoroutineFactory
import pytest

from radikopodcast.database.models import Program
from radikopodcast.radiko_archiver import RadikoArchiver


class TestRadikoArchiver:
    """Test for RadikoArchiver."""

    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    def test(self) -> None:
        self.mock_ffmpeg_coroutine_again()
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        asyncio.run(RadikoArchiver().archive(program))

    @staticmethod
    @pytest.mark.asyncio()
    @pytest.mark.skipif(sys.platform == "win32", reason="test for Linux only")
    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    async def test_with_process_task_pool_executor() -> None:
        """ProcessTaskPoolExecutor should shutdown when raise KeyboardInterrupt.

        During running RadikoArchiver.archive().
        """
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        radiko_archiver = RadikoArchiver()
        # Reason: To test that process can teardown when running asynchronous task
        with pytest.raises(KeyboardInterrupt):  # noqa: PT012, SIM117
            with ProcessTaskPoolExecutor() as executor:
                executor.create_process_task(radiko_archiver.archive, program)
                raise KeyboardInterrupt

    @pytest.mark.skipif(sys.platform == "win32", reason="test for Linux only")
    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    @pytest.mark.parametrize("type_error", [FileExistsError, KeyboardInterrupt])
    def test_error(self, type_error: type[BaseException]) -> None:
        """Specific error should not catch in method: archive()."""
        ffmpeg_coroutine = self.mock_ffmpeg_coroutine_again()
        # Reason: Creating mock.
        ffmpeg_coroutine.execute.side_effect = type_error  # type: ignore[attr-defined]
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        with pytest.raises(type_error):
            asyncio.run(RadikoArchiver(stop_if_file_exists=True).archive(program))

    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    def test_file_exists_skip(self) -> None:
        ffmpeg_coroutine = self.mock_ffmpeg_coroutine_again()
        # Reason: Creating mock.
        ffmpeg_coroutine.execute.side_effect = FileExistsError  # type: ignore[attr-defined]
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        asyncio.run(RadikoArchiver().archive(program))

    @staticmethod
    def mock_ffmpeg_coroutine_again() -> FFmpegCoroutine:
        """To fix execute as AsyncMock.

        Method execute seems to reset as PicklableMock...
        """
        ffmpeg_coroutine = FFmpegCoroutineFactory.create()
        # Reason: Creating mock.
        ffmpeg_coroutine.execute = AsyncMock()  # type: ignore[method-assign]
        return ffmpeg_coroutine
