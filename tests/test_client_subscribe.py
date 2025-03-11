import pytest

from src.ntfy_api.client import NtfyClient
from src.ntfy_api.creds import Credentials
from src.ntfy_api.filter import Filter
from src.ntfy_api.subscription import NtfySubscription


def _client() -> NtfyClient:
    return NtfyClient(
        base_url="https://www.example.com",
        default_topic="default_topic",
        credentials=Credentials(basic=("user", "pass")),
    )


def test_subscribe() -> None:
    f = Filter()
    client = _client()
    sub = client.subscribe(filter=f, max_queue_size=10)
    assert isinstance(sub, NtfySubscription)
    assert sub.base_url == "https://www.example.com"
    assert sub.topics == ("default_topic",)
    assert sub.credentials is client.credentials
    assert sub.filter is f
    assert sub.max_queue_size == 10


def test_subscribe_no_topic() -> None:
    with pytest.raises(ValueError):
        NtfyClient(base_url="https://www.example.com").subscribe()


def test_subscribe_single_topic() -> None:
    assert _client().subscribe(topics="topic").topics == ("topic",)


def test_subscribe_multiple_topics() -> None:
    assert _client().subscribe(topics=("t1", "t2")).topics == ("t1", "t2")
