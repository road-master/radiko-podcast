# Copyright (C) 2026 Master
"""Test for radiko_archiver.py."""

import asyncio
import sys
from typing import cast
from unittest.mock import AsyncMock

import pytest
from asynccpu.process_task_pool_executor import ProcessTaskPoolExecutor
from pytest_mock import MockFixture
from radikoplaylist.exceptions import BadHttpStatusCodeError
from radikoplaylist.exceptions import NoAvailableUrlError
from requests.exceptions import ConnectionError as RequestsConnectionError
from sqlalchemy import and_

from radikopodcast.archive_workflow import MAX_ARCHIVE_RETRY_COUNT
from radikopodcast.archive_workflow import RadikoArchiveWorkflow
from radikopodcast.database.models import ArchiveStatusId
from radikopodcast.database.models import Program
from radikopodcast.database.session_manager import SessionManager
from radikopodcast.output_directory import OutputDirectory
from radikopodcast.programaggregate.factory import RadikoProgramAggregateToArchiveFactory
from radikopodcast.programaggregate.timefree30 import RadikoProgramAggregateToArchiveTimeFree30


class TestRadikoArchiver:
    """Test for RadikoArchiver."""

    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    def test(self) -> None:
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        asyncio.run(RadikoArchiveWorkflow(RadikoProgramAggregateToArchiveFactory(OutputDirectory())).execute(program))

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="test for Linux only")
    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    async def test_with_process_task_pool_executor() -> None:
        """ProcessTaskPoolExecutor should shutdown when raise KeyboardInterrupt.

        During running RadikoArchiver.archive().
        """
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        radiko_archiver = RadikoArchiveWorkflow(RadikoProgramAggregateToArchiveFactory(OutputDirectory()))
        # Reason: To test that process can teardown when running asynchronous task
        with pytest.raises(KeyboardInterrupt):  # noqa: PT012, SIM117
            with ProcessTaskPoolExecutor() as executor:
                executor.create_process_task(radiko_archiver.execute, program)
                raise KeyboardInterrupt

    @pytest.mark.skipif(sys.platform == "win32", reason="test for Linux only")
    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    @pytest.mark.parametrize("type_error", [FileExistsError, KeyboardInterrupt])
    def test_error(self, type_error: type[BaseException]) -> None:
        """Specific error should not catch in method: archive()."""
        factory = RadikoProgramAggregateToArchiveFactory(OutputDirectory())
        # Reason: Creating mock.
        factory.ffmpeg_coroutine.execute.side_effect = type_error  # type: ignore[attr-defined]
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        with pytest.raises(type_error):
            asyncio.run(RadikoArchiveWorkflow(factory, stop_if_file_exists=True).execute(program))

    @pytest.mark.usefixtures("record_program", "mock_master_playlist_client", "mock_ffmpeg_coroutine")
    def test_file_exists_skip(self) -> None:
        factory = RadikoProgramAggregateToArchiveFactory(OutputDirectory())
        # Reason: Creating mock.
        factory.ffmpeg_coroutine.execute.side_effect = FileExistsError  # type: ignore[attr-defined]
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        asyncio.run(RadikoArchiveWorkflow(factory).execute(program))

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("record_program")
    async def test_timefree30_branch(self, mocker: MockFixture) -> None:
        """When radiko_session is set, RadikoProgramAggregateToArchiveTimeFree30.archive() should be called."""
        mock_archive = mocker.patch.object(RadikoProgramAggregateToArchiveTimeFree30, "archive", new=AsyncMock())
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        factory = RadikoProgramAggregateToArchiveFactory(OutputDirectory(), radiko_session="session_token")
        radiko_archive_workflow = RadikoArchiveWorkflow(factory)
        await radiko_archive_workflow.execute(program)
        mock_archive.assert_called_once()
        assert radiko_archive_workflow.radiko_program_aggregate_factory.radiko_session == "session_token"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("record_program")
    async def test_no_available_url_skip(self, mocker: MockFixture) -> None:
        """NoAvailableUrlError should mark program as failed without raising, without touching the retry count."""
        mocker.patch.object(
            RadikoProgramAggregateToArchiveFactory,
            "create",
            side_effect=NoAvailableUrlError([]),
        )
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        await RadikoArchiveWorkflow(RadikoProgramAggregateToArchiveFactory(OutputDirectory())).execute(program)
        found = self.find_one("ROPPONGI PASSION PIT")
        assert found.archive_status == ArchiveStatusId.FAILED.value
        assert found.archive_retry_count == 0

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("record_program")
    async def test_bad_http_status_code_retry(
        self,
        mocker: MockFixture,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """BadHttpStatusCodeError should requeue the program as archivable without raising."""
        mocker.patch.object(
            RadikoProgramAggregateToArchiveFactory,
            "create",
            side_effect=BadHttpStatusCodeError("failed in https://example.com/playlist.m3u8."),
        )
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        await RadikoArchiveWorkflow(RadikoProgramAggregateToArchiveFactory(OutputDirectory())).execute(program)
        found = self.find_one("ROPPONGI PASSION PIT")
        assert found.archive_status == ArchiveStatusId.ARCHIVABLE.value
        assert found.archive_retry_count == 1
        assert "attempt 1/5" in caplog.text
        assert "https://example.com/playlist.m3u8" in caplog.text

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("record_program")
    async def test_connection_error_retry(
        self,
        mocker: MockFixture,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """RequestsConnectionError should requeue the program as archivable without raising."""
        mocker.patch.object(
            RadikoProgramAggregateToArchiveFactory,
            "create",
            side_effect=RequestsConnectionError(),
        )
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        await RadikoArchiveWorkflow(RadikoProgramAggregateToArchiveFactory(OutputDirectory())).execute(program)
        found = self.find_one("ROPPONGI PASSION PIT")
        assert found.archive_status == ArchiveStatusId.ARCHIVABLE.value
        assert found.archive_retry_count == 1
        assert "will retry next cycle" in caplog.text

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("record_program_retried")
    async def test_retry_exhausted(
        self,
        mocker: MockFixture,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Once retries are exhausted, the program should be marked failed with an ERROR log."""
        mocker.patch.object(
            RadikoProgramAggregateToArchiveFactory,
            "create",
            side_effect=RequestsConnectionError(),
        )
        program = Program.find(["ROPPONGI PASSION PIT"])[0]
        await RadikoArchiveWorkflow(RadikoProgramAggregateToArchiveFactory(OutputDirectory())).execute(program)
        found = self.find_one("ROPPONGI PASSION PIT")
        assert found.archive_status == ArchiveStatusId.FAILED.value
        assert found.archive_retry_count == MAX_ARCHIVE_RETRY_COUNT
        assert "Giving up" in caplog.text

    @staticmethod
    def find_one(keyword: str) -> Program:
        with SessionManager() as session:
            list_condition_keyword = [Program.title.like(f"%{keyword}%")]
            return cast(
                "Program",
                session.query(Program).filter(and_(*list_condition_keyword)).order_by(Program.ft.asc()).first(),
            )
