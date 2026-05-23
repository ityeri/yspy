from __future__ import annotations

from dataclasses import dataclass

from yspy.utils import get_by_path

from .exceptions import PageParsingException


@dataclass
class CommentComponent:
    comment: str
    author_url: str
    author_display_name: str

    @staticmethod
    def from_json(raw_data: dict) -> CommentComponent:
        try:
            return CommentComponent(
                comment=get_by_path(raw_data, 'payload commentEntityPayload properties content content'),
                author_url='https://youtube.com' + get_by_path(
                    raw_data,
                    'payload commentEntityPayload author channelCommand innertubeCommand browseEndpoint canonicalBaseUrl'
                ),
                author_display_name=get_by_path(raw_data, 'payload commentEntityPayload author displayName')
            )
        except KeyError:
            raise PageParsingException('The given data is not a comment component data')
        except IndexError:
            raise PageParsingException('The given data is not a comment component data')

@dataclass
class CommentsPage:
    comments: list[CommentComponent]
    comment_continuation_token: str

    @staticmethod
    def from_json(raw_data: dict[str, dict]) -> CommentsPage:
        raw_components: list[dict] = get_by_path(raw_data, 'frameworkUpdates entityBatchUpdate mutations')

        comment_components = list()

        for raw_component in raw_components:
            try:
                comment_components.append(CommentComponent.from_json(raw_component))
            except PageParsingException:
                pass

        first_page_token_path = [
            'onResponseReceivedEndpoints', -1, 'reloadContinuationItemsCommand',
            'continuationItems', -1, 'continuationItemRenderer',
            'continuationEndpoint continuationCommand token'
        ]
        next_page_token_path = [
            'onResponseReceivedEndpoints', -1, 'appendContinuationItemAction',
            'continuationItems', -1, 'continuationItemRenderer',
            'continuationEndpoint continuationCommand token'
        ]

        try:
            continuation_key = get_by_path(raw_data, *first_page_token_path)
        except KeyError:
            continuation_key = get_by_path(raw_data, *next_page_token_path)
        except IndexError:
            continuation_key = get_by_path(raw_data, *next_page_token_path)

        return CommentsPage(
            comments=comment_components,
            comment_continuation_token=continuation_key
        )
