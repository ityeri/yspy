import json
from pathlib import Path

import pytest

TEST_DATAS = Path(__file__).parent / 'test_datas'


def load_fixture(name):
    with open(TEST_DATAS / name, encoding='utf-8') as f:
        return json.load(f)



from yspy.data_parsing.channel import ChannelDetailPage


def test_parse_channel_detail_page():
    page = ChannelDetailPage.from_json(load_fixture('channel_detail_page.json'))

    assert page.id == 'UCg7rkxrTnIhiHEpXY1ec9NA'
    assert page.url == 'http://www.youtube.com/@sleepground'
    assert page.country == '대한민국'
    assert page.subscriber_count_text == '구독자 238만명'
    assert page.view_count_text == '조회수 4,372,270,606회'
    assert page.joined_date_text == '가입일: 2014. 5. 23.'
    assert page.video_count_text == '동영상 4,514개'
    assert len(page.links) == 3
