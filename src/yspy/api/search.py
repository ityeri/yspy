from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient

from .search_result import SearchResult, VideoResult, ChannelResult, from_search_result_component
from yspy.data_parsing.search_result import SearchResultPage, ChannelComponent
from yspy.request import SearchResultRequest
from yspy.utils import SearchMode, Locale, ENGLISH_LOCALE


@dataclass
class Search:
    results: list[SearchResult]
    continuation_token: str

    @staticmethod
    async def asearch(
            query: str, search_mode: SearchMode, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Search:
        response = await SearchResultRequest.aget_first_page(query, search_mode, locale, client=client)
        search_result_page = SearchResultPage.from_json(response.json())

        search_result_page_eng = None
        if locale != ENGLISH_LOCALE:
            # numeric fields are parsed from the English page — same pattern as Channel.aget
            eng_response = await SearchResultRequest.aget_first_page(
                query, search_mode, ENGLISH_LOCALE, client=client
            )
            search_result_page_eng = SearchResultPage.from_json(eng_response.json())

        return Search.from_search_result_page(search_result_page, search_result_page_eng, locale)

    @staticmethod
    def from_search_result_page(
            search_result_page: SearchResultPage,
            search_result_page_eng: SearchResultPage | None = None,
            locale: Locale | None = None
    ) -> Search:
        eng_components: dict[str, ChannelComponent] | None = None
        if search_result_page_eng is not None:
            eng_components = {
                component.id: component
                for component in search_result_page_eng.components
                if isinstance(component, ChannelComponent)
            }
        return Search(
            results=[
                from_search_result_component(component, eng_components, locale)
                for component in search_result_page.components
            ],
            continuation_token=search_result_page.continuation_token
        )

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

    async def amore(
            self, search_mode: SearchMode, locale: Locale | None = None, *, client: AsyncClient | None = None
    ) -> Search:
        response = await SearchResultRequest.aget_continuation_page(
            self.continuation_token, search_mode, locale, client=client
        )
        search_result_page = SearchResultPage.from_json(response.json())

        search_result_page_eng = None
        if locale != ENGLISH_LOCALE:
            eng_response = await SearchResultRequest.aget_continuation_page(
                self.continuation_token, search_mode, ENGLISH_LOCALE, client=client
            )
            search_result_page_eng = SearchResultPage.from_json(eng_response.json())

        return Search.from_search_result_page(search_result_page, search_result_page_eng, locale)
