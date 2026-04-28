from __future__ import annotations

from dataclasses import dataclass

from .video_component import VideoComponent
from .channel_component import ChannelComponent
from .search_result_component import SearchResultComponent
from yspy.utils import get_by_path


@dataclass
class SearchResultPage:
    components: list[SearchResultComponent]
    continuation_token: str


    @staticmethod
    def parse_components(raw_data: dict[str, dict]) -> list[SearchResultComponent]:
        if 'videoRenderer' in raw_data:
            return [VideoComponent.from_json(raw_data)]
        elif 'channelRenderer' in raw_data:
            return [ChannelComponent.from_json(raw_data)]
        elif 'shelfRenderer' in raw_data:
            inner_data = get_by_path(raw_data, 'shelfRenderer content verticalListRenderer items')
            return list(map(SearchResultPage.parse_components, inner_data))
        else:
            return []

    @staticmethod
    def from_json(raw_data: dict[str, dict], is_continuation_page: bool) -> SearchResultPage:
        if not is_continuation_page:
            try:
                inner_data = get_by_path(
                    raw_data,
                    'contents twoColumnSearchResultsRenderer primaryContents sectionListRenderer contents'
                )
            except KeyError:
                raise ValueError('Given json data is a continuation page data or not a search result page data')
        else:
            try:
                inner_data = get_by_path(
                    raw_data, 'onResponseReceivedCommands', 0, 'appendContinuationItemsAction continuationItems'
                )
            except KeyError:
                raise ValueError('Given json data is not a continuation page data')
            except IndexError:
                raise ValueError('Given json data is not a continuation page data')

        item_section_data = next(filter(lambda c: 'itemSectionRenderer' in c, inner_data))
        content_data = get_by_path(item_section_data, 'itemSectionRenderer contents')
        continuation_data = next(filter(lambda c: 'continuationItemRenderer' in c, inner_data))

        nested_components = [SearchResultPage.parse_components(element) for element in content_data]

        return SearchResultPage(
            components=[component for components in nested_components for component in components],
            continuation_token=get_by_path(
                continuation_data,
                'continuationItemRenderer continuationEndpoint continuationCommand token'
            )
        )