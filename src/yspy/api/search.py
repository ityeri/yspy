from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient

from yspy.data_parsing.search_result import SearchResultPage, SearchResultComponent, VideoComponent, ChannelComponent
from yspy.request import SearchResultRequest
from yspy.utils import SearchMode


@dataclass
class Search:
    results: list[SearchResultComponent]
    videos: list[VideoComponent]
    channels: list[ChannelComponent]

    @staticmethod
    async def asearch(query: str, search_mode: SearchMode, *, client: AsyncClient | None = None) -> Search:
        response = await SearchResultRequest.aget_first_page(query, search_mode, client=client)
        search_result_page = SearchResultPage.from_json(response.json())

        return Search.from_search_result_page(search_result_page)

    @staticmethod
    def from_search_result_page(search_result_page: SearchResultPage):
        return Search(
            results=search_result_page.components,
            videos=[video for video in search_result_page.components if isinstance(video, VideoComponent)],
            channels=[channel for channel in search_result_page.components if isinstance(channel, ChannelComponent)]
        )
