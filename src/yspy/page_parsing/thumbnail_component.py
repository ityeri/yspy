from dataclasses import dataclass


@dataclass(frozen=True)
class ThumbnailComponent:
    url: str
    width: int
    height: int
