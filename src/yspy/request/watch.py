from httpx import AsyncClient, Response, Client

from .constants import WATCH_URL, BASE_HEADERS
from .utils import optional_async_client, optional_sync_client


class WatchRequest:
    # The watch page HTML carries the ytcfg (VISITOR_DATA / api key) and, when
    # not bot-gated, an embedded ytInitialPlayerResponse with the playability
    # status — both useful for the availability check of a video.
    @staticmethod
    def get_page(video_id: str, *, client: Client | None = None) -> Response:
        with optional_sync_client(client) as client:
            return client.get(
                WATCH_URL,
                params={'v': video_id},
                headers={**BASE_HEADERS, 'Accept-Language': 'en-US,en;q=0.9'},
                follow_redirects=True,
            )

    @staticmethod
    async def aget_page(video_id: str, *, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await client.get(
                WATCH_URL,
                params={'v': video_id},
                headers={**BASE_HEADERS, 'Accept-Language': 'en-US,en;q=0.9'},
                follow_redirects=True,
            )
