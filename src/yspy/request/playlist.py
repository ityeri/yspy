from httpx import AsyncClient

from .utils import optional_async_client, build_browse_url, BASE_HEADERS, build_request_body


async def get_first_page(playlist_id: str, client: AsyncClient | None = None) -> dict[str, dict]:
    async with optional_async_client(client) as client:
        response = await client.post(
            url=build_browse_url(),
            json=build_request_body({
                'browseId': 'VL' + playlist_id if not playlist_id.startswith('VL') else playlist_id
            }),
            headers=BASE_HEADERS
        )

        return response.json()

async def get_continuation_page(continuation_token: str, client: AsyncClient | None = None) -> dict[str, dict]:
    async with optional_async_client(client) as client:
        response = await client.post(
            url=build_browse_url(),
            json=build_request_body({
                'continuation': continuation_token
            }),
            headers=BASE_HEADERS
        )

        return response.json()
