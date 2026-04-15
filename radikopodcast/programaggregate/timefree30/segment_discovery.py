"""Re-export for backward compatibility.

Use radikopodcast.programaggregate.segment.discovery instead.
"""

from radikopodcast.programaggregate.segment.discovery import MasterPlaylistRequestFactory
from radikopodcast.programaggregate.segment.discovery import MediaPlaylistText
from radikopodcast.programaggregate.segment.discovery import SegmentsDiscovery
from radikopodcast.programaggregate.segment.discovery import fetch_media_playlist_text
from radikopodcast.programaggregate.segment.discovery import get_segment_datetimes

__all__ = [
    "MasterPlaylistRequestFactory",
    "MediaPlaylistText",
    "SegmentsDiscovery",
    "fetch_media_playlist_text",
    "get_segment_datetimes",
]
