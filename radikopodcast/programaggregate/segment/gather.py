# Copyright (C) 2026 Master
"""Gather helper that consumes sibling results on failure."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar
from typing import cast

if TYPE_CHECKING:
    from collections.abc import Awaitable
    from collections.abc import Iterable

T = TypeVar("T")


class SiblingConsumingGather(Generic[T]):
    """Gathers awaitables, consuming every sibling's result when one fails.

    Prevents "Future exception was never retrieved" warnings: when one awaitable fails, siblings are cancelled and
    their results are consumed before the original exception is re-raised.
    """

    def __init__(self, awaitables: Iterable[Awaitable[T]]) -> None:
        self.futures = [asyncio.ensure_future(awaitable) for awaitable in awaitables]

    async def run(self) -> list[T]:
        """Gather the futures, re-raising the first exception after draining siblings."""
        try:
            return cast("list[T]", await asyncio.gather(*self.futures))
        except BaseException:
            self._cancel_siblings()
            await asyncio.gather(*self.futures, return_exceptions=True)
            raise

    def _cancel_siblings(self) -> None:
        for future in self.futures:
            future.cancel()
