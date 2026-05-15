from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path, get_by_path_or
from .channel_component import ChannelComponent
from .search_result_component import SearchResultComponent
from .video_component import VideoComponent


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
            nested_components = [SearchResultPage.parse_components(element) for element in inner_data]
            return [component for components in nested_components for component in components]

        else:
            return []

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> SearchResultPage:
        try:
            inner_data = get_by_path_or(
                raw_data,
                'contents twoColumnSearchResultsRenderer primaryContents sectionListRenderer contents'
            )
            if inner_data is None:
                inner_data = get_by_path(
                    raw_data, 'onResponseReceivedCommands', 0, 'appendContinuationItemsAction continuationItems'
                )
        except KeyError:
            raise ValueError('The given data is not a search result page data')
        except IndexError:
            raise ValueError('The given data is not a search result page data')

        continuation_data = next(filter(lambda c: 'continuationItemRenderer' in c, inner_data))

        item_section_data = next(filter(lambda c: 'itemSectionRenderer' in c, inner_data))
        raw_components = get_by_path(item_section_data, 'itemSectionRenderer contents')
        components = [SearchResultPage.parse_components(element) for element in raw_components]
        components = [component for components in components for component in components]

        return SearchResultPage(
            components=components,
            continuation_token=get_by_path(
                continuation_data,
                'continuationItemRenderer continuationEndpoint continuationCommand token'
            )
        )
