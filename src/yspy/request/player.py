from httpx import AsyncClient, Response, Client

from yspy.utils import Locale
from .utils import PLAYER_API_URL, BASE_HEADERS
from .utils import optional_async_client, optional_sync_client, RequestData


class PlayerRequest:
    @staticmethod
    def build_request(
            video_id: str,
            locale: Locale | None = None,
            *,
            client_data: dict[str, str | bool] | None = None,
            visitor_data: str | None = None,
            headers: dict[str, str] | None = None
    ) -> RequestData:
        # client_data/visitor_data/headers override the default WEB client so a
        # caller can walk the pot-free fallback clients (PLAYER_FALLBACK_CLIENTS)
        return RequestData(
            method='POST',
            endpoint=PLAYER_API_URL,
            payload_params={
                'videoId': video_id,
                'contentCheckOk': True,
                'racyCheckOk': True
            },
            locale=locale,
            client_data=client_data,
            visitor_data=visitor_data,
            headers=headers or BASE_HEADERS
        )

    @staticmethod
    def get_page(
            video_id: str,
            locale: Locale | None = None,
            *,
            client_data: dict[str, str | bool] | None = None,
            visitor_data: str | None = None,
            headers: dict[str, str] | None = None,
            client: Client | None = None
    ) -> Response:
        with optional_sync_client(client) as client:
            return PlayerRequest.build_request(
                video_id, locale, client_data=client_data, visitor_data=visitor_data, headers=headers
            ).send_sync_request(client)

    @staticmethod
    async def aget_page(
            video_id: str,
            locale: Locale | None = None,
            *,
            client_data: dict[str, str | bool] | None = None,
            visitor_data: str | None = None,
            headers: dict[str, str] | None = None,
            client: AsyncClient | None = None
    ) -> Response:
        async with optional_async_client(client) as client:
            return await PlayerRequest.build_request(
                video_id, locale, client_data=client_data, visitor_data=visitor_data, headers=headers
            ).send_async_request(client)
