def get_by_path(data: str | dict | list, path: str) -> str | dict | list:
    path_parts = path.split()

    if len(path_parts) == 0:
        return data
    else:
        return get_by_path(data[path_parts[0]], ' '.join(path_parts[1:]))


__all__ = [
    'get_by_path'
]