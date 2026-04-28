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
        return get_by_path(data[path_parts[0]], *path_parts[:1])


__all__ = [
    'get_by_path'
]