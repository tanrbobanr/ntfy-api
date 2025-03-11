import pytest

from src.ntfy_api.enums import Priority, Tag
from src.ntfy_api.filter import Filter


def test_filter() -> None:
    assert Filter(
        since=12345,
        scheduled=True,
        id="ID",
        title="title",
        priority=Priority.urgent,
        tags=(Tag.a, Tag.b),
    ).serialize() == {
        "X-Since": "12345",
        "X-Scheduled": "1",
        "X-ID": "ID",
        "X-Title": "title",
        "X-Priority": "5",
        "X-Tags": "a,b",
    }


def test_unknown_type() -> None:
    with pytest.raises(TypeError):
        Filter(since=4.2).serialize()
