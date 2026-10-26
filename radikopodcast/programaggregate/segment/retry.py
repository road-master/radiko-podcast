# Copyright (C) 2026 Master
"""Per-segment retry for transient radiko request errors."""

from __future__ import annotations

import asyncio
from logging import getLogger
from typing import TYPE_CHECKING
from typing import TypeVar

import aiohttp
from radikoplaylist.exceptions import HttpRequestError
from requests.exceptions import ConnectionError as RequestsConnectionError

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Callable

T = TypeVar("T")

TRANSIENT_ERRORS = (HttpRequestError, RequestsConnectionError, aiohttp.ClientError, TimeoutError)


class TransientErrorRetry:
    """Retries one segment request with exponential backoff so a sporadic 502 doesn't fail the whole program.

    The final attempt's exception propagates unchanged, so callers keep their existing error handling.
    """

    def __init__(self, max_attempts: int = 4, base_delay_seconds: float = 1.0) -> None:
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.logger = getLogger(__name__)

    async def run(self, func: Callable[[], Awaitable[T]], attempt: int = 1) -> T:
        """Await func, retrying on transient errors until max_attempts is reached."""
        if attempt >= self.max_attempts:
            return await func()
        try:
            return await func()
        except TRANSIENT_ERRORS as error:
            await self._back_off(attempt, error)
        return await self.run(func, attempt + 1)

    async def _back_off(self, attempt: int, error: Exception) -> None:
        delay = self.base_delay_seconds * 2 ** (attempt - 1)
        self.logger.warning(
            "Transient error (attempt %d/%d), retrying in %.1fs: %s",
            attempt,
            self.max_attempts,
            delay,
            error,
        )
        await asyncio.sleep(delay)
