from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient, Client

from yspy.data_parsing.search_result import SearchResultPage
from yspy.request import SearchResultRequest
from yspy.utils import SearchMode, Locale, ENGLISH_LOCALE, Language, Unspecified, NONE_LOCALE
from .search_result_element import SearchResultElement, VideoResultElement, ChannelResultElement, \
    from_search_result_component


@dataclass
class Search:
    results: list[SearchResultElement]
    search_mode: SearchMode | None
    locale: Locale
    continuation_token: str

    @staticmethod
    def search(
            query: str, search_mode: SearchMode | None = None, locale: Locale = NONE_LOCALE,
            *,
            client: Client | None = None
    ) -> Search:
        response = SearchResultRequest.get_first_page(query, search_mode, locale, client=client)
        search_result_page = SearchResultPage.from_json(response.json())

        if locale.language != Language.ENGLISH:
            eng_response = SearchResultRequest.get_first_page(query, search_mode, ENGLISH_LOCALE, client=client)
            eng_search_result_page = SearchResultPage.from_json(eng_response.json())
        else:
            eng_search_result_page = search_result_page

        return Search.from_search_result_page(search_result_page, eng_search_result_page, search_mode, locale)

    @staticmethod
    async def asearch(
            query: str, search_mode: SearchMode | None = None, locale: Locale = NONE_LOCALE,
            *,
            client: AsyncClient | None = None
    ) -> Search:
        response = await SearchResultRequest.aget_first_page(query, search_mode, locale, client=client)
        search_result_page = SearchResultPage.from_json(response.json())

        if locale.language != Language.ENGLISH:
            eng_response = await SearchResultRequest.aget_first_page(query, search_mode, ENGLISH_LOCALE, client=client)
            eng_search_result_page = SearchResultPage.from_json(eng_response.json())
        else:
            eng_search_result_page = search_result_page

        return Search.from_search_result_page(search_result_page, eng_search_result_page, search_mode, locale)

    @staticmethod
    def from_search_result_page(
            search_result_page: SearchResultPage,
            eng_search_result_page: SearchResultPage,
            search_mode: SearchMode | None = None,
            locale: Locale = NONE_LOCALE
    ) -> Search:
        return Search(
            results=[
                from_search_result_component(component, eng_component, locale)
                for (component, eng_component) in zip(search_result_page.components, eng_search_result_page.components)
            ],
            search_mode=search_mode,
            locale=locale,
            continuation_token=search_result_page.continuation_token
        )

    def more(
            self,
            search_mode: SearchMode | None | Unspecified = Unspecified(),
            locale: Locale | Unspecified = Unspecified(),
            *,
            client: Client | None = None
    ) -> Search:
        actual_search_mode: SearchMode | None = search_mode if search_mode != Unspecified() else self.search_mode
        actual_locale: Locale = locale if locale != Unspecified() else self.locale

        response = SearchResultRequest.get_continuation_page(
            self.continuation_token, actual_search_mode, actual_locale, client=client
        )
        search_result_page = SearchResultPage.from_json(response.json())

        if actual_locale.language != Language.ENGLISH:
            eng_response = SearchResultRequest.get_continuation_page(
                self.continuation_token, actual_search_mode, ENGLISH_LOCALE, client=client
            )
            eng_search_result_page = SearchResultPage.from_json(eng_response.json())
        else:
            eng_search_result_page = search_result_page

        return Search.from_search_result_page(
            search_result_page, eng_search_result_page, actual_search_mode, actual_locale
        )

    async def amore(
            self,
            search_mode: SearchMode | None | Unspecified = Unspecified(),
            locale: Locale | Unspecified = Unspecified(),
            *,
            client: AsyncClient | None = None
    ) -> Search:
        actual_search_mode: SearchMode | None = search_mode if search_mode != Unspecified() else self.search_mode
        actual_locale: Locale = locale if locale != Unspecified() else self.locale

        response = await SearchResultRequest.aget_continuation_page(
            self.continuation_token, actual_search_mode, actual_locale, client=client
        )
        search_result_page = SearchResultPage.from_json(response.json())

        if actual_locale.language != Language.ENGLISH:
            eng_response = await SearchResultRequest.aget_continuation_page(
                self.continuation_token, actual_search_mode, ENGLISH_LOCALE, client=client
            )
            eng_search_result_page = SearchResultPage.from_json(eng_response.json())
        else:
            eng_search_result_page = search_result_page

        return Search.from_search_result_page(
            search_result_page, eng_search_result_page, actual_search_mode, actual_locale
        )

    @property
    def videos(self) -> list[VideoResultElement]:
        return [result for result in self.results if isinstance(result, VideoResultElement)]

    @property
    def channels(self) -> list[ChannelResultElement]:
        return [result for result in self.results if isinstance(result, ChannelResultElement)]

    def first_or(self, default: SearchResultElement | None) -> SearchResultElement | None:
        try:
            return self.results[0]
        except IndexError:
            return default

    def first_video_or(self, default: VideoResultElement | None) -> VideoResultElement | None:
        try:
            return self.videos[0]
        except IndexError:
            return default

    def first_channel_or(self, default: ChannelResultElement | None) -> ChannelResultElement | None:
        try:
            return self.channels[0]
        except IndexError:
            return default
