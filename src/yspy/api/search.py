from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient, Client

from yspy.data_parsing.search_result import SearchResultPage, SearchResultComponent, VideoComponent, ChannelComponent
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
            eng_search_result_page: SearchResultPage | None = None,
            search_mode: SearchMode | None = None,
            locale: Locale = NONE_LOCALE
    ) -> Search:
        # position of components differ between locale and english pages (ad drops, ranking)
        # so components are paired by their own id (videoId / channel browseId)
        if eng_search_result_page is None:
            eng_by_id: dict[str, SearchResultComponent] = {}
        else:
            eng_by_id = {
                Search._component_key(component): component
                for component in eng_search_result_page.components
            }

        return Search(
            results=[
                from_search_result_component(
                    component, eng_by_id.get(Search._component_key(component), component), locale
                )
                for component in search_result_page.components
            ],
            search_mode=search_mode,
            locale=locale,
            continuation_token=search_result_page.continuation_token
        )

    def more(
            self,
            search_mode: SearchMode | None | Unspecified = Unspecified(),
            locale: Locale | None = None,
            *,
            client: Client | None = None
    ) -> Search:
        actual_search_mode: SearchMode | None = search_mode if search_mode != Unspecified() else self.search_mode
        actual_locale: Locale = self.locale if locale is None else locale

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
            locale: Locale | None = None,
            *,
            client: AsyncClient | None = None
    ) -> Search:
        actual_search_mode: SearchMode | None = search_mode if search_mode != Unspecified() else self.search_mode
        actual_locale: Locale = self.locale if locale is None else locale

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

    @staticmethod
    def _component_key(component: SearchResultComponent) -> str:
        if isinstance(component, VideoComponent):
            return f'video:{component.id}'
        elif isinstance(component, ChannelComponent):
            return f'channel:{component.id}'
        else:
            raise TypeError('Unknown type SearchResultComponent has passed')
