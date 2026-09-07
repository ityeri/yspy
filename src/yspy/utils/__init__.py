from enum import Enum

from yarl import URL

from .i18n import Language, Region, Locale, ENGLISH_LOCALE, NONE_LOCALE

YOUTUBE_BASE_URL = URL('https://youtube.com')


def get_by_path(data: str | dict | list, *path: str | int) -> str | dict | list:
    path_parts = list()

    for path_chunk in path:
        if isinstance(path_chunk, str):
            path_parts.extend(path_chunk.split())
        elif isinstance(path_chunk, int):
            path_parts.append(path_chunk)

    if len(path_parts) == 0:
        return data
    else:
        return get_by_path(data[path_parts[0]], *path_parts[1:])


def get_by_path_or(
        data: str | dict | list | None,
        *path: str | int,
        default: str | dict | list | None = None
) -> str | dict | list | None:
    if data is None:
        return None

    try:
        return get_by_path(data, *path)
    except KeyError:
        return default
    except IndexError:
        return default


def to_youtube_url(url: str | URL) -> str:
    url = URL(url)

    if not url.is_absolute():
        return str(YOUTUBE_BASE_URL.join(url))
    else:
        return str(url)


class SearchMode(str, Enum):
    VIDEO = 'EgIQAQ%3D%3D'
    CHANNEL = 'EgIQAg%3D%3D'
    PLAYLIST = 'EgIQAw%3D%3D'
    LIVESTREAM = 'EgJAAQ%3D%3D'


class Unspecified:
    def __eq__(self, other):
        if isinstance(other, Unspecified):
            return True
        else:
            return False

    def __init_subclass__(cls, **kwargs):
        raise TypeError(f'cannot subclass {cls.__name__}')


__all__ = [
    'get_by_path',
    'get_by_path_or',
    'to_youtube_url',

    'Language',
    'Region',
    'Locale',
    'NONE_LOCALE',
    'ENGLISH_LOCALE',

    'Unspecified',

    'SearchMode',
]
