from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path

from .exceptions import PageParsingException


@dataclass
class VideoNextPage:
    comment_continuation_token: str

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> VideoNextPage:
        try:
            return VideoNextPage(
                comment_continuation_token=get_by_path(
                    raw_data,
                    'engagementPanels', 0, 'engagementPanelSectionListRenderer content sectionListRenderer',
                    'contents', 0, 'itemSectionRenderer',
                    'contents', 0,
                    'continuationItemRenderer continuationEndpoint continuationCommand token'
                )
            )
        except KeyError:
            raise PageParsingException('The given data is not a video continuation page')