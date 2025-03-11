import unittest.mock

import pytest

from src.ntfy_api.client import NtfyClient
from src.ntfy_api.creds import Credentials
from src.ntfy_api.errors import APIError
from src.ntfy_api.message import Message

from . import mocks


def _read(filename: str) -> bytes:
    with open(f"tests/responses/{filename}", "rb") as infile:
        return infile.read()


def _client() -> NtfyClient:
    return NtfyClient(
        base_url="https://www.example.com",
        default_topic="default_topic",
        credentials=Credentials(basic=("user", "pass")),
    )


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_publish_standalone_message_headers() -> None:
    """Check to ensure headers are correctly included from the
    serialized message.

    """
    resp: mocks.httpx.Response = _client().publish(msg=Message(title="title"))
    assert resp.status_code == 200
    assert resp.standalone
    assert resp.capture.url == "https://www.example.com/default_topic"
    assert resp.capture.headers and resp.capture.headers == {
        "X-Title": "title",
        "Authorization": "Basic dXNlcjpwYXNz",
    }
    assert resp.capture.json is None
    assert resp.capture.data is None
    assert resp.capture.content is None


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_publish_standalone_default_topic() -> None:
    """Make sure default topic is used if neither message nor
    `.publish()` are given topics.

    """
    resp: mocks.httpx.Response = _client().publish(msg=Message())
    assert resp.status_code == 200
    assert resp.standalone
    assert resp.capture.url == "https://www.example.com/default_topic"
    assert resp.capture.headers and resp.capture.headers == {
        "Authorization": "Basic dXNlcjpwYXNz",
    }
    assert resp.capture.json is None
    assert resp.capture.data is None
    assert resp.capture.content is None


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_publish_standalone_message_topic() -> None:
    """Ensure message topic overrides default topic"""
    resp: mocks.httpx.Response = _client().publish(
        msg=Message(topic="message_topic")
    )
    assert resp.status_code == 200
    assert resp.standalone
    assert resp.capture.url == "https://www.example.com/message_topic"
    assert resp.capture.headers and resp.capture.headers == {
        "Authorization": "Basic dXNlcjpwYXNz",
    }
    assert resp.capture.json is None
    assert resp.capture.data is None
    assert resp.capture.content is None


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_publish_standalone_custom_topic() -> None:
    """Ensure custom topic overrides default topic"""
    resp: mocks.httpx.Response = _client().publish(
        msg=Message(), topic="custom_topic"
    )
    assert resp.status_code == 200
    assert resp.standalone
    assert resp.capture.url == "https://www.example.com/custom_topic"
    assert resp.capture.headers and resp.capture.headers == {
        "Authorization": "Basic dXNlcjpwYXNz",
    }
    assert resp.capture.json is None
    assert resp.capture.data is None
    assert resp.capture.content is None


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_publish_standalone_custom_topic_with_message_topic() -> None:
    """Ensure custom topic does not override message topic"""
    resp: mocks.httpx.Response = _client().publish(
        msg=Message(topic="message_topic"), topic="custom_topic"
    )
    assert resp.status_code == 200
    assert resp.standalone
    assert resp.capture.url == "https://www.example.com/message_topic"
    assert resp.capture.headers and resp.capture.headers == {
        "Authorization": "Basic dXNlcjpwYXNz",
    }
    assert resp.capture.json is None
    assert resp.capture.data is None
    assert resp.capture.content is None


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_publish_standalone_custom_topic_override() -> None:
    """Ensure custom topic overrides message topic if override=True"""
    resp: mocks.httpx.Response = _client().publish(
        msg=Message(topic="message_topic"),
        topic="custom_topic",
        topic_override=True,
    )
    assert resp.status_code == 200
    assert resp.standalone
    assert resp.capture.url == "https://www.example.com/custom_topic"
    assert resp.capture.headers and resp.capture.headers == {
        "Authorization": "Basic dXNlcjpwYXNz",
    }
    assert resp.capture.json is None
    assert resp.capture.data is None
    assert resp.capture.content is None


@unittest.mock.patch("src.ntfy_api.client.httpx", mocks.httpx)
def test_publish_standalone_no_topic() -> None:
    """Ensure error is thrown if no topic is found"""
    with pytest.raises(ValueError):
        NtfyClient(base_url="https://www.example.com").publish(msg=Message())


def test_publish_standalone_error() -> None:
    """Ensure error is thrown on non-200 HTTP status code"""
    m = mocks.httpx.Client(standalone=True)
    m.set_status("post", 400)
    m.set_content("post", _read("sent_error.txt"))
    with unittest.mock.patch("src.ntfy_api.client.httpx.post", m.post):
        with pytest.raises(APIError):
            _client().publish(msg=Message())
    assert m.captures[0]._response_.status_code == 400
