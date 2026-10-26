# Copyright (C) 2026 Master
"""Tests for retry.py."""

from __future__ import annotations

import pytest
from radikoplaylist.exceptions import BadHttpStatusCodeError

from radikopodcast.programaggregate.segment.retry import TransientErrorRetry

MAX_ATTEMPTS = 4


class FlakyCall:
    """Callable failing with a given exception for the first N calls, then returning a value."""

    def __init__(self, failures: int, error: Exception) -> None:
        self.failures = failures
        self.error = error
        self.calls = 0

    async def __call__(self) -> str:
        self.calls += 1
        if self.calls <= self.failures:
            raise self.error
        return "ok"


class TestTransientErrorRetry:
    """Tests for TransientErrorRetry."""

    @pytest.mark.asyncio
    async def test_run(self) -> None:
        """Should return the result after transient errors as long as attempts remain."""
        flaky = FlakyCall(MAX_ATTEMPTS - 1, BadHttpStatusCodeError("failed in url."))
        assert await TransientErrorRetry(max_attempts=MAX_ATTEMPTS, base_delay_seconds=0).run(flaky) == "ok"
        assert flaky.calls == MAX_ATTEMPTS

    @pytest.mark.asyncio
    async def test_run_raises_after_max_attempts(self) -> None:
        """Should re-raise the last transient error once max_attempts is exhausted."""
        flaky = FlakyCall(MAX_ATTEMPTS, BadHttpStatusCodeError("failed in url."))
        with pytest.raises(BadHttpStatusCodeError):
            await TransientErrorRetry(max_attempts=MAX_ATTEMPTS, base_delay_seconds=0).run(flaky)
        assert flaky.calls == MAX_ATTEMPTS

    @pytest.mark.asyncio
    async def test_run_does_not_retry_non_transient_error(self) -> None:
        """Should propagate a non-transient error immediately without retrying."""
        flaky = FlakyCall(1, ValueError("boom"))
        with pytest.raises(ValueError, match="boom"):
            await TransientErrorRetry(max_attempts=MAX_ATTEMPTS, base_delay_seconds=0).run(flaky)
        assert flaky.calls == 1
