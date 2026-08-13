from __future__ import annotations

from dataclasses import dataclass

from httpx import AsyncClient
from yarl import URL

from yspy.data_parsing import CommentComponent, VideoNextPage, CommentsPage
from yspy.request import VideoNextRequest, CommentsRequest


@dataclass
class Comments:
    comments: list[CommentComponent]
    continuation_token: str

    @staticmethod
    async def aget(
            *, video_id: str | None = None, video_url: str | None = None, client: AsyncClient | None
    ) -> Comments:
        if video_id is not None and video_url is not None:
            raise ValueError('Only one of the parameters, video_id or video_url, should be passed')
        if video_url is not None:
            video_id = URL(video_url).query['v']

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
