import json
from pathlib import Path

from yspy.page_parsing import SearchResultPage

with open(Path(__file__).parent / 'test_datas/nested_search_result.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

page_data = SearchResultPage.from_json(raw_data, is_continuation_page=False)

breakpoint()
