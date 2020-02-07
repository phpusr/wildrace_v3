from datetime import datetime
from typing import Iterable, Optional


def find(lst: Iterable, action):
    result = find_all(lst, action)
    if result:
        return result[0]


def find_all(lst: Iterable, action):
    return list(filter(action, lst))


def remove_non_utf8_chars(text: Optional[str]) -> Optional[str]:
    if text is None:
        return None

    return bytes(text, 'utf-8').decode('utf-8', 'ignore')


def get_count_days(start_date: Optional[datetime], end_date: Optional[datetime]):
    if not start_date or not end_date:
        return None

    if start_date > end_date:
        raise RuntimeError('start_date > end_date')

    return (end_date - start_date).days + 1
