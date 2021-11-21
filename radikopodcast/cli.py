"""Console script for radikopodcast."""
import asyncio
import sys
from pathlib import Path
from typing import NoReturn, Optional

import click

from radikopodcast.radiko_podcast import RadikoPodcast


@click.command()
@click.option(
    "-f", "--file", type=click.Path(exists=True, resolve_path=True, path_type=Path), default=Path("config.yml")
)
def radiko_podcast(file: Optional[Path]) -> NoReturn:
    """Console script for radiko Podcast."""
    podcast = RadikoPodcast(path_to_configuration=file)
    try:
        podcast.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        sys.exit(130)
    sys.exit(1)  # pragma: no cover
