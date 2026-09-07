from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path_or

from .channel_component import ChannelComponent
from .search_result_component import SearchResultComponent
from .video_component import VideoComponent
from ..exceptions import DataParsingException


@dataclass
class SearchResultPage:
    components: list[SearchResultComponent]
    continuation_token: str | None

    @staticmethod
    def parse_components(raw_data: dict[str, dict]) -> list[SearchResultComponent]:
        try:
            if 'videoRenderer' in raw_data:
                return [VideoComponent.from_json(raw_data)]

            elif 'channelRenderer' in raw_data:
                return [ChannelComponent.from_json(raw_data)]

            elif 'shelfRenderer' in raw_data:
                inner_data = get_by_path_or(raw_data, 'shelfRenderer content verticalListRenderer items')
                if inner_data is None:
                    inner_data = get_by_path_or(raw_data, 'shelfRenderer content horizontalListRenderer items')

                nested_components = [SearchResultPage.parse_components(element) for element in inner_data]
                return [component for components in nested_components for component in components]

            else:
                return []
        except (KeyError, DataParsingException):
            # ad rows or half-broken renderers are not search results — drop them silently
            return []

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> SearchResultPage:
        inner_data = get_by_path_or(
            raw_data,
            'contents twoColumnSearchResultsRenderer primaryContents sectionListRenderer contents'
        )
        if inner_data is None:
            inner_data = get_by_path_or(
                raw_data, 'onResponseReceivedCommands', 0, 'appendContinuationItemsAction continuationItems'
            )

        if inner_data is None:
            # not a search result page (e.g. the last continuation page) — treat it as an empty page
            return SearchResultPage(components=[], continuation_token=None)

        continuation_token = None
        components = []

        for element in inner_data:
            if 'continuationItemRenderer' in element:
                continuation_token = get_by_path_or(
                    element, 'continuationItemRenderer continuationEndpoint continuationCommand token'
                )
            elif 'itemSectionRenderer' in element:
                raw_components = get_by_path_or(element, 'itemSectionRenderer contents')
                if raw_components is None:
                    continue

                nested_components = [SearchResultPage.parse_components(element) for element in raw_components]
                components.extend(component for components in nested_components for component in components)

        return SearchResultPage(components=components, continuation_token=continuation_token)
