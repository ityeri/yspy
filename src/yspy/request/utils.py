from contextlib import asynccontextmanager
from typing import Optional, AsyncIterator
from urllib.parse import urlencode

import httpx
from httpx import AsyncClient


BASE_REQUEST_BODY = {
    'context': {
        'client': {
            'clientName': 'WEB',
            'clientVersion': '2.20210224.06.00',
            'newVisitorCookie': True,
        },
        'user': {
            'lockedSafetyMode': False,
        }
    }
}

USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/70.0.3538.77 Safari/537.36'
)

BASE_HEADERS = {
    'User-Agent': USER_AGENT
}

BROWSE_API_URL = 'https://www.youtube.com/youtubei/v1/browse'
BROWSE_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'


def build_browse_url(parameters: dict[str, str] = None) -> str:
    if parameters is None:
        parameters = {}
    return (
            'https://www.youtube.com/youtubei/v1/browse'
            + '?' + urlencode({'key': BROWSE_KEY} | parameters)
    )

@asynccontextmanager
async def optional_async_client(client: AsyncClient | None = None) -> AsyncIterator[httpx.AsyncClient]:
    is_injected = client is not None
    inner_client = client if is_injected else httpx.AsyncClient()

    try:
        yield inner_client
    finally:
        if not is_injected:
            await inner_client.aclose()
