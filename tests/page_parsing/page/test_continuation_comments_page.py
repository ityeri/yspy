import json
from pathlib import Path

from yspy.page_parsing import ContinuationCommentsPage

with open(Path(__file__).parent / 'test_datas/continuation_comments_page.json', 'r') as f:
    raw_data = json.load(f)

continuation_comments_page = ContinuationCommentsPage.from_json(raw_data)

breakpoint()
