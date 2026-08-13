from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient

from .search_result import SearchResult, VideoResult, ChannelResult, from_search_result_component
from yspy.data_parsing.search_result import SearchResultPage
from yspy.request import SearchResultRequest
from yspy.utils import SearchMode, Locale


@dataclass
class Search:
    results: list[SearchResult]

    @property
    def videos(self) -> list[VideoResult]:
        return [result for result in self.results if isinstance(result, VideoResult)]
    @property
    def channels(self) -> list[ChannelResult]:
        return [result for result in self.results if isinstance(result, ChannelResult)]

    def first_or(self, default: SearchResult | None) -> SearchResult | None:
        try: return self.results[0]
        except IndexError: return default

    def first_video_or(self, default: VideoResult | None) -> VideoResult | None:
        try: return self.videos[0]
        except IndexError: return default
    def first_channel_or(self, default: ChannelResult | None) -> ChannelResult | None:
        try: return self.channels[0]
        except IndexError: return default

    @staticmethod
    async def asearch(
            query: str, search_mode: SearchMode, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Search:
        response = await SearchResultRequest.aget_first_page(query, search_mode, locale, client=client)
        search_result_page = SearchResultPage.from_json(response.json())

        return Search.from_search_result_page(search_result_page, locale)

    @staticmethod
    def from_search_result_page(search_result_page: SearchResultPage, locale: Locale | None = None):
        return Search(
            results=[from_search_result_component(component, locale) for component in search_result_page.components]
        )
