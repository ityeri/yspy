from httpx import AsyncClient, Response, Client

from yspy.utils import Locale
from .constants import PLAYER_API_URL
from .utils import optional_async_client, optional_sync_client, RequestData


class VideoRequest:
    @staticmethod
    def build_request(video_id: str, locale: Locale | None = None) -> RequestData:
        return RequestData(
            method='POST',
            endpoint=PLAYER_API_URL,
            payload_params={
                'videoId': video_id,
                'contentCheckOk': True,
                'racyCheckOk': True
            },
            locale=locale
        )

    @staticmethod
    def get_page(video_id: str, locale: Locale | None = None, *, client: Client | None = None) -> Response:
        with optional_sync_client(client) as client:
            return VideoRequest.build_request(video_id, locale).send_sync_request(client)

    @staticmethod
    async def aget_page(video_id: str, locale: Locale | None = None, *, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await VideoRequest.build_request(video_id, locale).send_async_request(client)
