# Copyright (C) 2026 Master
"""Tests for gather.py."""

from __future__ import annotations

import asyncio

import pytest

from radikopodcast.programaggregate.segment.gather import SiblingConsumingGather


class TestSiblingConsumingGather:
    """Tests for SiblingConsumingGather."""

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Should return results in order when every awaitable succeeds."""

        async def value(number: int) -> int:
            return number

        assert await SiblingConsumingGather([value(1), value(2)]).run() == [1, 2]

    @pytest.mark.asyncio
    async def test_run_raises_first_exception_and_consumes_siblings(self) -> None:
        """Should re-raise the first exception and leave no sibling future unretrieved."""

        async def fail_fast() -> None:
            message = "boom"
            raise ValueError(message)

        async def fail_slow() -> None:
            await asyncio.sleep(0.05)
            message = "late boom"
            raise RuntimeError(message)

        gather = SiblingConsumingGather([fail_slow(), fail_fast()])
        with pytest.raises(ValueError, match="boom"):
            await gather.run()
        assert all(future.done() for future in gather.futures)

    @pytest.mark.asyncio
    async def test_run_cancel(self) -> None:
        """Should propagate cancellation when the caller cancels the gathering task."""

        async def wait_forever() -> None:
            await asyncio.sleep(3600)

        task = asyncio.ensure_future(SiblingConsumingGather([wait_forever(), wait_forever()]).run())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
