"""Tests for cli.py."""
import re
from unittest import mock

import pytest
from click.testing import CliRunner
from freezegun.api import freeze_time
from pytest import LogCaptureFixture

from radikopodcast import cli
from radikopodcast.radiko_podcast import RadikoPodcast


@pytest.mark.usefixtures("mock_all")
# Decorator: freeze_time without tick=True breaks EventLoop.run_in_executor().
# see:
#  - Hangs in multiprocessing · Issue #230 · spulec/freezegun
#    https://github.com/spulec/freezegun/issues/230#issuecomment-835721924
@freeze_time("2021-01-17 05:16:00", tz_offset=-9, tick=True)
def test_command_line_interface(runner_in_isolated_filesystem: CliRunner) -> None:
    """Test CLI."""
    with mock.patch.object(RadikoPodcast, "sleep", side_effect=KeyboardInterrupt):
        result = runner_in_isolated_filesystem.invoke(cli.radiko_podcast)
    assert result.output == ""
    assert result.exit_code == 130
    help_result = runner_in_isolated_filesystem.invoke(cli.radiko_podcast, ["--help"])
    assert help_result.exit_code == 0
    assert "--help           Show this message and exit." in help_result.output


@pytest.mark.usefixtures("database_session", "mock_requests_station")
@freeze_time("2021-01-17 05:15:00", tz_offset=-9)
def test_command_line_interface_error(runner_in_isolated_filesystem: CliRunner, caplog: LogCaptureFixture) -> None:
    """Test CLI when error."""
    with mock.patch.object(RadikoPodcast, "sleep", side_effect=IOError):
        result = runner_in_isolated_filesystem.invoke(cli.radiko_podcast)
    assert result.output == ""
    assert result.exit_code == 1
    pattern = re.compile(r"ERROR.*OSError$", flags=re.DOTALL | re.MULTILINE)
    assert pattern.search(caplog.text)
