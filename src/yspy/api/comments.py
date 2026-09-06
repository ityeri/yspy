from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient
from yarl import URL

from yspy.api.exceptions import VideoIdentifierException
from yspy.data_parsing import CommentComponent, VideoNextPage, CommentsPage
from yspy.request import VideoNextRequest, CommentsRequest


@dataclass
class Comments:
    comments: list[CommentComponent]
    continuation_token: str

    @staticmethod
    async def aget(video_id_or_url: str, *, client: AsyncClient | None = None) -> Comments:
        if len(video_id_or_url) == 11:
            video_id = video_id_or_url
        else:
            try:
                video_id = URL(video_id_or_url).query['v']
            except KeyError:
                raise VideoIdentifierException('The given video_id_or_url is neither a URL nor a video ID')

        response = await VideoNextRequest.aget_page(video_id, client=client)
        video_next_page = VideoNextPage.from_json(response.json())

        response = await CommentsRequest.aget_page(video_next_page.comment_continuation_token, client=client)
        comments_page = CommentsPage.from_json(response.json())

        return Comments(
            comments=comments_page.comments,
            continuation_token=comments_page.continuation_token
        )

    @staticmethod
    def from_comments_page(comments_page: CommentsPage) -> Comments:
        return Comments(
            comments=comments_page.comments,
            continuation_token=comments_page.continuation_token
        )

    async def amore(self, *, client: AsyncClient | None) -> Comments:
        response = await CommentsRequest.aget_page(self.continuation_token, client=client)
        comments_page = CommentsPage.from_json(response.json())

        return Comments(
            comments=comments_page.comments,
            continuation_token=comments_page.continuation_token
        )
