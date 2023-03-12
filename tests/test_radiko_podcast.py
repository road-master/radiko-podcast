"""Tests for radiko_podcast.py."""
import asyncio
from pathlib import Path
import sys
from unittest import mock

from freezegun.api import freeze_time
import pytest

from radikopodcast.radiko_podcast import RadikoPodcast


class TestRadikoPodcast:
    """Test for RadikoPodcast."""

    @staticmethod
    @pytest.mark.skipif(sys.platform == "win32", reason="test for Linux only")
    @pytest.mark.usefixtures("_mock_all")
    # Decorator: freeze_time without tick=True breaks EventLoop.run_in_executor().
    # This comment prevents Pylint duplicate-code.
    # see:
    #  - Hangs in multiprocessing · Issue #230 · spulec/freezegun
    #    https://github.com/spulec/freezegun/issues/230#issuecomment-835721924
    @freeze_time("2021-01-17 05:16:00", tz_offset=-9, tick=True)
    def test(config_yaml: Path) -> None:
        """RadikoPodcast should stop when raise KeyboardInterrupt."""
        podcast = RadikoPodcast(path_to_configuration=config_yaml)
        with (
            pytest.raises(KeyboardInterrupt),
            mock.patch.object(RadikoPodcast, "sleep", side_effect=KeyboardInterrupt),
        ):
            podcast.run()

    @staticmethod
    def test_sleep() -> None:
        asyncio.run(RadikoPodcast.sleep(0.1))
