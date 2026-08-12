from httpx import AsyncClient, Response

from .constants import BROWSE_API_URL, BASE_HEADERS
from .utils import optional_async_client, RequestData


class PlaylistRequest:
    @staticmethod
    async def get_first_page(playlist_id: str, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await RequestData(
                method='POST',
                endpoint=BROWSE_API_URL,
                payload_params={'browseId': 'VL' + playlist_id if not playlist_id.startswith('VL') else playlist_id},
                headers=BASE_HEADERS
            ).send_request(client)

    @staticmethod
    async def get_continuation_page(continuation_token: str, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await RequestData(
                method='POST',
                endpoint=BROWSE_API_URL,
                payload_params={'continuation': continuation_token},
                headers=BASE_HEADERS
            ).send_request(client)
