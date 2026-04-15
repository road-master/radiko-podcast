"""Radiko Time Free 30 program archiver."""

from __future__ import annotations

from typing import TYPE_CHECKING

from radikoplaylist import TimeFree30DayMasterPlaylistRequest

from radikopodcast.programaggregate.slowapi import RadikoProgramAggregateToArchiveSlowApi

if TYPE_CHECKING:
    from radikopodcast.database.models import Program
    from radikopodcast.output_directory import OutputDirectory


class RadikoProgramAggregateToArchiveTimeFree30(RadikoProgramAggregateToArchiveSlowApi):
    """Program aggregate for 30-day time-free download.

    Thin subclass of RadikoProgramAggregateToArchiveSlowApi that uses the TimeFree30DayMasterPlaylistRequest (type=c)
    for 30-day timefree access.
    """

    def __init__(self, program: Program, output_directory: OutputDirectory, radiko_session: str) -> None:
        super().__init__(program, output_directory, radiko_session, TimeFree30DayMasterPlaylistRequest)
