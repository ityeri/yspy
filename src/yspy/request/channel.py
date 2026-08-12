from httpx import AsyncClient, Response

from .utils import optional_async_client, RequestData, BROWSE_API_URL


class ChannelRequest:
    @staticmethod
    async def get_page(channel_id: str, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await RequestData(
                method='POST',
                endpoint=BROWSE_API_URL,
                payload_params={'browseId': channel_id}
            ).send_request(client)

    @staticmethod
    async def get_detail_page(continuation_token: str, client: AsyncClient | None = None) -> Response:
        async with optional_async_client(client) as client:
            return await RequestData(
                method='POST',
                endpoint=BROWSE_API_URL,
                payload_params={'continuation': continuation_token}
            ).send_request(client)
