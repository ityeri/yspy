from __future__ import annotations

import re
from datetime import date


_COUNT_UNITS = {
    'k': 1_000,
    'm': 1_000_000,
    'b': 1_000_000_000,
    'thousand': 1_000,
    'million': 1_000_000,
    'billion': 1_000_000_000,
}

_COUNT_PATTERN = re.compile(
    r'(?P<number>\d+(?:[.,]\d+)?)\s*(?P<unit>[kmb]|[a-z]+)?',
    re.IGNORECASE,
)

def _parse_count(text: str | None) -> int | None:
    if not text:
        return None

    match = _COUNT_PATTERN.search(text.replace(',', ''))
    if match is None:
        return None

    number = float(match.group('number'))
    unit = (match.group('unit') or '').lower()
    multiplier = _COUNT_UNITS.get(unit, _COUNT_UNITS.get(unit[:1], 1))

    return int(number * multiplier)

def parse_subscriber_count(text: str | None) -> int | None:
    if not text:
        return None
    if re.search(r'\bno\s+subscribers?\b', text, re.IGNORECASE):
        return 0
    return _parse_count(text)

def parse_view_count(text: str | None) -> int | None:
    if not text:
        return None
    if re.search(r'\bno\s+views?\b', text, re.IGNORECASE):
        return 0
    return _parse_count(text)

def parse_video_count(text: str | None) -> int | None:
    if not text:
        return None
    if re.search(r'\bno\s+videos?\b', text, re.IGNORECASE):
        return 0
    return _parse_count(text)

_MONTH_ABBR = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}
def parse_joined_date(text: str | None) -> date | None:
    if not text:
        return None

    match = re.search(r'([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})', text)
    if match and match.group(1).lower()[:3] in _MONTH_ABBR:
        return date(int(match.group(3)), _MONTH_ABBR[match.group(1).lower()[:3]], int(match.group(2)))

    return None
